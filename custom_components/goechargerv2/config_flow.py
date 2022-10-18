"""Go-eCharger config flow setup"""
from typing import Any, Literal
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, OptionsFlow, ConfigFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_NAME, CONF_HOST, CONF_API_TOKEN
from .const import DOMAIN


def _get_config_values(data_input: dict) -> dict:
    data = {}
    config = [CONF_NAME, CONF_HOST, CONF_API_TOKEN, CONF_SCAN_INTERVAL]

    for config_name in config:
        data[config_name] = data_input.get(config_name)

    return data


def _get_config_schema(default_values: dict) -> dict:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=default_values.get(CONF_NAME, None)): str,
            vol.Required(CONF_HOST, default=default_values.get(CONF_HOST, None)): str,
            vol.Required(
                CONF_API_TOKEN, default=default_values.get(CONF_API_TOKEN, None)
            ): str,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=default_values.get(CONF_SCAN_INTERVAL, 10),
            ): int,
        }
    )


class GoeChargerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the Go-eCharger component."""

    VERSION: Literal[1] = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return GoeChargerOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME),
                data=_get_config_values(user_input),
                options=_get_config_values(user_input),
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_get_config_schema({CONF_SCAN_INTERVAL: 10}),
        )


class GoeChargerOptionsFlowHandler(OptionsFlow):
    """Config flow options handler for iss."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry: ConfigEntry = config_entry
        self.options: dict[str, Any] = dict(config_entry.options)

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="init",
            data_schema=_get_config_schema(
                {
                    CONF_NAME: self.config_entry.options.get(CONF_NAME),
                    CONF_HOST: self.config_entry.options.get(CONF_HOST),
                    CONF_API_TOKEN: self.config_entry.options.get(CONF_API_TOKEN),
                    CONF_SCAN_INTERVAL: self.config_entry.options.get(
                        CONF_SCAN_INTERVAL
                    ),
                }
            ),
        )
