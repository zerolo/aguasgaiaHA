import logging

from aguasgaia import AguasGaia
from .const import CONF_PASSWORD, CONF_USERNAME, CONF_SUBSCRIPTIONID, DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

__version__ = "0.0.5"
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

PLATFORMS: list[str] = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """ Setting up the API """
    _LOGGER.debug("Starting setting up API")

    configDetails = config.get(DOMAIN) or {}

    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass, True)
    api = AguasGaia(session, configDetails.get(CONF_USERNAME), configDetails.get(CONF_PASSWORD), configDetails.get(CONF_SUBSCRIPTIONID))

    _LOGGER.debug("Saving API into hass.data[DOMAIN]")

    hass.data[DOMAIN] = {
        "api": api
    }
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ Setup component from given entry """
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ Reload Config Entry """
    await async_setup_entry(hass, entry)