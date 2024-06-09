from datetime import timedelta
import logging
from typing import Any, Dict

import aiohttp
from .const import (
    CONF_SUBSCRIPTIONID,
    DOMAIN, 
    PRICE_ENTITY,
    CONSUMPTION_ENTITY,
    DEFAULT_MONETARY_ICON,
    DEFAULT_CONSUMPTION_ICON,
    UNIT_OF_MEASUREMENT_EURO,
    UNIT_OF_MEASUREMENT_WATER,
    ATTRIBUTION,
    CONF_USERNAME,
    CONF_PASSWORD
)
from aguasgaia import AguasGaia

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# API Poll time
SCAN_INTERVAL = timedelta(hours=12)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """ Setup Sensors"""
    _LOGGER.debug("Setup Entry")

    session = async_get_clientsession(hass, True)
    api = AguasGaia(session, config_entry.data.get(CONF_USERNAME), config_entry.data.get(CONF_PASSWORD), config_entry.data.get(CONF_SUBSCRIPTIONID))

    sensors = [AguasGaiaSensor(api, PRICE_ENTITY), AguasGaiaSensor(api, CONSUMPTION_ENTITY)]

    async_add_entities(sensors, update_before_add=True)


class AguasGaiaSensor(SensorEntity):
    """ Aguas de Gaia sensor representation """

    def __init__(self, api: AguasGaia, sensorType: str):
        _LOGGER.debug("Init  %s",sensorType)
        super().__init__()
        self._api = api
        self._sensorType = sensorType
        self._invoice = None
        self._consumption = None
        self._entity_name = self._sensorType+"_"+self._api.get_selected_subscription()
        self._state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self._available = True

        if sensorType == PRICE_ENTITY:
            self._icon = DEFAULT_MONETARY_ICON
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_EURO
            self._device_class = SensorDeviceClass.MONETARY
        elif sensorType == CONSUMPTION_ENTITY:
            self._icon = DEFAULT_CONSUMPTION_ICON
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_WATER
            self._device_class = SensorDeviceClass.WATER
            self._state_class = SensorStateClass.TOTAL
            

    @property
    def name(self) ->  str:
        """ Entity Name """
        return self._entity_name
    
    @property
    def unique_id(self) -> str:
        """ Sensor unique id """
        return f"{DOMAIN}__{self._entity_name}"
    
    @property
    def available(self) -> bool:
        return self._available
    
    @property
    def state(self) -> float:
        return self._state
    
    @property
    def device_class(self):
        return self._device_class
    
    @property
    def state_class(self):
        return self._state_class
    
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def attribution(self):
        return ATTRIBUTION
    
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        if self._sensorType == PRICE_ENTITY:
            if self._invoice:
                return self._invoice.invoice_attributes
        elif self._sensorType == CONSUMPTION_ENTITY:
            if self._consumption:
                return self._consumption.consumption_attributes
        return {}

    async def async_update(self) -> None:
        _LOGGER.debug("Update %s",self._sensorType)
        try:
            await self._api.login()
            if self._sensorType == PRICE_ENTITY:
                self._invoice = await self._api.get_last_invoice()
                _LOGGER.debug("invoice %s",self._invoice)
                if self._invoice:
                    self._state = round(self._invoice.invoice_value, 2) 
            elif self._sensorType == CONSUMPTION_ENTITY:
                self._consumption = await self._api.get_last_consumption()
                _LOGGER.debug("consumption %s",self._consumption)
                if self._consumption:
                    self._state = round(self._consumption.consumption_value, 2) 
            else:
                self._state = 99
        except aiohttp.ClientError as err:
            self._available = False
            _LOGGER.error("Error retrieving data from Aguas de Gaia API: %s", err)
    
