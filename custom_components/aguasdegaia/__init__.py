import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

__version__ = "0.0.94"
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ Setup component from given entry """
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ Unload Config Entry """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """ Reload Config Entry """
    await hass.config_entries.async_reload(entry.entry_id) 