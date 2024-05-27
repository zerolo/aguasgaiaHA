import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API, CONF_PASSWORD, CONF_USERNAME, CONF_SUBSCRIPTIONID, DOMAIN

from aguasgaia import AguasGaia


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

DATA_SCHEMA = vol.Schema(
    { 
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_SUBSCRIPTIONID): str
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Aguas de Gaia config flow """
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """ Handle a flow from user interface """
        _LOGGER.debug("Start config flow ")

        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input.get(CONF_USERNAME))
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass, True)
            api = AguasGaia(session, user_input.get(CONF_USERNAME), user_input.get(CONF_PASSWORD), user_input.get(CONF_SUBSCRIPTIONID))
            connOK = await api.login()
            if connOK:
                _LOGGER.debug("Login Succeeded")
                return self.async_create_entry(
                    title=user_input.get(CONF_USERNAME)+" - "+api.get_selected_subscription(),
                    data={
                        **user_input,
                        API: api
                    }
                )
            else:
                errors = {
                    "base": "invalid_login"
                }
        
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )
    