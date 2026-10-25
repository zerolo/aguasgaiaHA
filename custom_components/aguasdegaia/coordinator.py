from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aguasgaia import AguasGaia
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SUBSCRIPTIONID,
    CONF_USERNAME,
    CONSUMPTION_ENTITY,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    PRICE_ENTITY,
)

_LOGGER = logging.getLogger(__name__)


def login_succeeded(api: AguasGaia, result: bool | None) -> bool:
    """Return True only when the API actually issued an authentication token."""
    return bool(result) and bool(getattr(api, "_token", None))


class AguasGaiaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch both sensors once per poll with a single API session."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                hours=entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS
                )
            ),
        )
        self.entry = entry
        self.api = AguasGaia(
            async_get_clientsession(hass),
            entry.data.get(CONF_USERNAME),
            entry.data.get(CONF_PASSWORD),
            entry.data.get(CONF_SUBSCRIPTIONID) or None,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            login_result = await self.api.login()
        except Exception as err:
            raise UpdateFailed(f"Error logging in to Aguas de Gaia: {err}") from err

        if login_result is False:
            raise ConfigEntryAuthFailed("Invalid Aguas de Gaia credentials")

        if not login_succeeded(self.api, login_result):
            raise UpdateFailed("Login to Aguas de Gaia failed")

        data: dict[str, Any] = dict(self.data or {})
        errors: list[str] = []

        try:
            invoice = await self.api.get_last_invoice()
        except Exception as err:
            errors.append(f"invoice: {err}")
            _LOGGER.warning("Error retrieving invoice from Aguas de Gaia: %s", err)
        else:
            if invoice is not None and getattr(invoice, "invoice_attributes", None):
                data[PRICE_ENTITY] = invoice
            else:
                data[PRICE_ENTITY] = None
                _LOGGER.debug("No invoice data returned by Aguas de Gaia")

        try:
            consumption = await self.api.get_last_consumption()
        except Exception as err:
            errors.append(f"consumption: {err}")
            _LOGGER.warning("Error retrieving consumption from Aguas de Gaia: %s", err)
        else:
            data[CONSUMPTION_ENTITY] = consumption if consumption is not None else None

        if len(errors) == 2:
            raise UpdateFailed(
                "Error retrieving data from Aguas de Gaia API: " + "; ".join(errors)
            )

        return data
