import logging
from typing import cast

import aiohttp
from aguasgaia import AguasGaia
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SUBSCRIPTIONID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    MAX_SCAN_INTERVAL_HOURS,
    MIN_SCAN_INTERVAL_HOURS,
)
from .coordinator import login_succeeded

_LOGGER = logging.getLogger(__name__)

PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
        vol.Optional(CONF_SUBSCRIPTIONID): str,
    }
)

REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Aguas de Gaia config flow."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle a flow from the user interface."""
        errors = {}

        if user_input is not None:
            user_input[CONF_SUBSCRIPTIONID] = (
                user_input.get(CONF_SUBSCRIPTIONID) or None
            )
            api = AguasGaia(
                async_get_clientsession(self.hass),
                user_input.get(CONF_USERNAME),
                user_input.get(CONF_PASSWORD),
                user_input.get(CONF_SUBSCRIPTIONID),
            )

            try:
                login_result = await api.login()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during Aguas de Gaia login")
                errors["base"] = "unknown"
            else:
                subscription_id = api.get_selected_subscription()
                if not login_succeeded(api, login_result) or subscription_id == "None":
                    errors["base"] = "invalid_login"
                else:
                    user_input[CONF_SUBSCRIPTIONID] = subscription_id
                    await self.async_set_unique_id(
                        f"{user_input.get(CONF_USERNAME)}_{subscription_id}"
                    )
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=(
                            user_input.get(CONF_USERNAME)
                            + " - "
                            + subscription_id
                        ),
                        data={**user_input},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Ask for a new password."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="reauth_failed")

        errors: dict[str, str] = {}

        if user_input is not None:
            api = AguasGaia(
                async_get_clientsession(self.hass),
                entry.data.get(CONF_USERNAME),
                user_input.get(CONF_PASSWORD),
                entry.data.get(CONF_SUBSCRIPTIONID),
            )

            try:
                login_result = await api.login()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during Aguas de Gaia reauth")
                errors["base"] = "unknown"
            else:
                if not login_succeeded(api, login_result):
                    errors["base"] = "invalid_login"
                else:
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data={
                            **entry.data,
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )
                    self.hass.config_entries.async_schedule_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=REAUTH_SCHEMA,
            errors=errors,
            description_placeholders={
                "username": entry.data.get(CONF_USERNAME, "")
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "AguasGaiaOptionsFlow":
        """Return the options flow."""
        return AguasGaiaOptionsFlow()


class AguasGaiaOptionsFlow(config_entries.OptionsFlow):
    """Aguas de Gaia options flow."""

    async def async_step_init(self, user_input=None):
        """Manage integration options."""
        entry = cast(
            ConfigEntry,
            self.hass.config_entries.async_get_entry(self.handler),
        )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL_HOURS,
                            max=MAX_SCAN_INTERVAL_HOURS,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="h",
                        )
                    )
                }
            ),
        )
