"""Go-eCharger integration"""

import logging
from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant import core
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from goecharger.goecharger import GoeChargerApi


from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_CHARGERS,
    CONF_API_URL,
    CONF_API_TOKEN,
    CHARGERS_API,
    COMMON_STATE,
)
from .state import StateFetcher
from .controller import ChargerController

_LOGGER = logging.getLogger(__name__)

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=10)

# Configuration validation
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_CHARGERS, default=[]): vol.All(
                    [
                        cv.ensure_list,
                        vol.All(
                            {
                                vol.Required(CONF_NAME): vol.All(cv.string),
                                vol.Required(CONF_API_URL): vol.All(cv.string),
                                vol.Required(CONF_API_TOKEN): vol.All(cv.string),
                            },
                            extra=vol.ALLOW_EXTRA,
                        ),
                    ],
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _setup_coordinator(state_fetcher_class, scan_interval, coordinator_name, hass):
    _LOGGER.debug("Configuring coordinator=%s", coordinator_name)

    state_fetcher = state_fetcher_class(hass)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=state_fetcher.fetch_states,
        update_interval=scan_interval,
    )
    state_fetcher.coordinator = coordinator
    hass.data[DOMAIN][coordinator_name] = coordinator

    return coordinator


def _setup_apis(config, hass):
    chargers_api = {}

    if DOMAIN in config:
        hass.data[DOMAIN] = {}
        scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        _LOGGER.debug("Scan interval set to=%s", scan_interval)

        chargers = config[DOMAIN].get(CONF_CHARGERS, [])
        _LOGGER.debug("Configured chargers=%s", chargers)

        for charger in chargers:
            name = charger[0][CONF_NAME]
            url = charger[0][CONF_API_URL]
            token = charger[0][CONF_API_TOKEN]
            _LOGGER.debug("Configuring API for the charger=%s", name)

            chargers_api[name] = GoeChargerApi(url, token)

    else:
        raise ValueError(f"Missing {DOMAIN} entry in the config")

    _LOGGER.debug("Configured charger APIs=%s", chargers_api)

    hass.data[DOMAIN][CHARGERS_API] = chargers_api

    return chargers_api


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up Go-eCharger platforms and services."""

    _LOGGER.info("Setting up the Go-eCharger integration")

    charger = ChargerController(hass)

    # expose services for other integrations
    hass.services.async_register(DOMAIN, "start_charging", charger.start_charging)
    hass.services.async_register(DOMAIN, "stop_charging", charger.stop_charging)
    hass.services.async_register(DOMAIN, "change_charging_power", charger.change_charging_power)
    hass.services.async_register(DOMAIN, "set_phase", charger.set_phase)
    hass.services.async_register(DOMAIN, "set_authentication", charger.set_authentication)


    scan_interval = DEFAULT_UPDATE_INTERVAL
    chargers_api = _setup_apis(config, hass)

    hass.data[DOMAIN][COMMON_STATE] = {"apis": chargers_api}

    charger_names = list(
        map(
            lambda charger: charger[0][CONF_NAME], config[DOMAIN].get(CONF_CHARGERS, [])
        )
    )

    for charger_name in charger_names:
        await _setup_coordinator(
            StateFetcher,
            scan_interval,
            charger_name + "_coordinator",
            hass,
        ).async_refresh()

    _LOGGER.info("Setup for the Go-eCharger integration completed")

    # load platform with sensors
    hass.async_create_task(
        async_load_platform(
            hass,
            "sensor",
            DOMAIN,
            {
                CONF_CHARGERS: charger_names,
            },
            config,
        )
    )

    return True
