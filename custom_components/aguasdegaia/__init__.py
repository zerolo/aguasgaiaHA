from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_SUBSCRIPTIONID,
    CONF_USERNAME,
    CONSUMPTION_ENTITY,
    CONSUMPTION_KEY,
    DOMAIN,
    PRICE_ENTITY,
    PRICE_KEY,
)
from .coordinator import AguasGaiaCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

CONFIG_ENTRY_VERSION = 2


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    coordinator = AguasGaiaCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry and entity unique IDs to stable identifiers."""
    if entry.version > CONFIG_ENTRY_VERSION:
        _LOGGER.error(
            "Cannot migrate Aguas de Gaia entry from version %s to %s",
            entry.version,
            CONFIG_ENTRY_VERSION,
        )
        return False

    if entry.version < CONFIG_ENTRY_VERSION:
        username = entry.data.get(CONF_USERNAME)
        subscription_id = entry.data.get(CONF_SUBSCRIPTIONID)

        if (
            username
            and subscription_id
            and str(subscription_id) != "None"
            and entry.unique_id != f"{username}_{subscription_id}"
        ):
            hass.config_entries.async_update_entry(
                entry, unique_id=f"{username}_{subscription_id}"
            )

        await er.async_migrate_entries(hass, entry.entry_id, _migrate_entity_entry)
        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)

    return True


def _migrate_entity_entry(entry: er.RegistryEntry) -> dict[str, str] | None:
    """Return the new unique ID for a legacy sensor entity."""
    if entry.unique_id.startswith(f"{DOMAIN}__{PRICE_ENTITY}_"):
        return {"new_unique_id": f"{entry.config_entry_id}_{PRICE_KEY}"}
    if entry.unique_id.startswith(f"{DOMAIN}__{CONSUMPTION_ENTITY}_"):
        return {"new_unique_id": f"{entry.config_entry_id}_{CONSUMPTION_KEY}"}
    return None


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
