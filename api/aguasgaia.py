import json
import logging
import aiohttp
from random import randint

from .const import DEFAULT_HEADERS, ENDPOINT, JSON_CONTENT, LASTDOC_PATH, LASTDOC_PATH_PARAM, LOGIN_PATH, PWD_PARAM, SUBSCRIPTIONS_PATH, USER_PARAM

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class AguasGaia:

    def __init__(self, websession, username, password):
        self.websession = websession
        self.username = username
        self.password = password

    async def initialize(self):
        _LOGGER.debug("AguasGaia API Initialize")
        await self.login()
        await self.getSubscriptions()
        return self
    
    async def login(self):
        _LOGGER.debug("AguasGaia API Login")
        url = ENDPOINT+LOGIN_PATH
        
        data = {
            USER_PARAM: self.username,
            PWD_PARAM: self.password
        }

        async with self.websession.post(url, headers=DEFAULT_HEADERS, json=data) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.token = res["token"]["token"]
                    self.session_cookies = ";".join(
                        list(
                            map(
                                lambda l: l.split(";")[0], 
                                response.headers.getall("Set-Cookie")
                            )
                        )
                    )
                    return res
                raise Exception("Can't login in the API")
            except aiohttp.ClientError as err:
                _LOGGER.error("Login error: %s", err)

    
    def getAuthHeaders(self):
        _LOGGER.debug("AguasGaia API AuthHeaders")
        return {
            **DEFAULT_HEADERS,
            "X-Auth-Token": self.token,
            "Cookie": self.session_cookies
        }
    
    async def getSubscriptions(self):
        _LOGGER.debug("AguasGaia API Subscriptions")
        url = ENDPOINT+SUBSCRIPTIONS_PATH
        headers = self.getAuthHeaders()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.subscriptions = res
                    self.selected_subscriptionID = str(res[0]["subscriptionId"])
                    return res
                raise Exception("Can't retrieve subscriptions")
            except aiohttp.ClientError as err:
                _LOGGER.error("Subscriptions Error: %s", err)
    
    async def getLastDocData(self):
        _LOGGER.debug("AguasGaia API LastDocData")
        url = ENDPOINT+LASTDOC_PATH+"?"+LASTDOC_PATH_PARAM+"="+self.selected_subscriptionID
        headers = self.getAuthHeaders()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.lastdocdata = res
                    return res
                raise Exception("Can't retrieve last document data")
            except aiohttp.ClientError as err:
                _LOGGER.error("last document data Error: %s", err)

    async def getInvoice(self):
        return randint(0,100)
    
    async def getConsumption(self):
        return randint(100,200)
    