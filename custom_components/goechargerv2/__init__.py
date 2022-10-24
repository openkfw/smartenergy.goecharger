"""Go-eCharger main integration file"""

import asyncio
import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from goechargerv2.goecharger import GoeChargerApi
from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    API,
    CHARGERS_API,
    CONF_CHARGERS,
    DOMAIN,
    INIT_STATE,
    UNSUB_OPTIONS_UPDATE_LISTENER,
)
from .controller import ChargerController
from .state import StateFetcher

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)

# Configuration validation
CONFIG_SCHEMA: vol.Schema = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_CHARGERS, default=[]): vol.All(
                    [
                        cv.ensure_list,
                        vol.All(
                            {
                                vol.Required(CONF_NAME): vol.All(cv.string),
                                vol.Required(CONF_HOST): vol.All(cv.string),
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


def _setup_coordinator(
    state_fetcher_class, scan_interval, coordinator_name, hass
) -> DataUpdateCoordinator:
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


def _setup_apis(config, hass) -> dict:
    chargers_api = {}

    if DOMAIN in config:
        hass.data[DOMAIN] = {}
        scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        _LOGGER.debug("Scan interval set to=%s", scan_interval)

        chargers = config[DOMAIN].get(CONF_CHARGERS, [])

        for charger in chargers:
            name = charger[0][CONF_NAME]
            url = charger[0][CONF_HOST]
            token = charger[0][CONF_API_TOKEN]
            _LOGGER.debug("Configuring API for the charger=%s", name)

            chargers_api[name] = {CONF_NAME: name, API: GoeChargerApi(url, token)}

    else:
        raise ValueError(f"Missing {DOMAIN} entry in the config")

    _LOGGER.debug("Configured charger APIs=%s", chargers_api)

    return chargers_api


async def async_setup_entry(
    hass: core.HomeAssistant, config_entry: ConfigEntry
) -> bool:
    """
    Sets up a charger defined via the UI. This includes:
    - setup of the API
    - coordinator
    - sensors
    """
    options = config_entry.options
    data = dict(config_entry.data)
    entry_id = config_entry.entry_id

    _LOGGER.debug(
        "Setting up a dynamic Go-eCharger charger with id=%s, data=%s and options=%s",
        entry_id,
        data,
        options,
    )

    # scan interval is provided as an integer, but has to be an interval
    scan_interval = timedelta(seconds=options[CONF_SCAN_INTERVAL])
    name = options[CONF_NAME]
    url = options[CONF_HOST]
    token = options[CONF_API_TOKEN]

    _LOGGER.debug("Configuring API for the charger=%s", entry_id)
    hass.data[DOMAIN][INIT_STATE][CHARGERS_API][entry_id] = {
        CONF_NAME: name,
        API: GoeChargerApi(url, token),
    }

    await _setup_coordinator(
        StateFetcher,
        scan_interval,
        f"{entry_id}_coordinator",
        hass,
    ).async_refresh()

    hass.data[DOMAIN][entry_id] = data

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    unsub_options_update_listener = config_entry.add_update_listener(
        options_update_listener
    )
    hass.data[DOMAIN][INIT_STATE][UNSUB_OPTIONS_UPDATE_LISTENER][
        entry_id
    ] = unsub_options_update_listener

    _LOGGER.debug("Setup for the dynamic Go-eCharger charger completed")

    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, config_entry: ConfigEntry
) -> bool:
    """Unload a config entry."""
    entry_id = config_entry.entry_id
    _LOGGER.debug("Unloading the charger=%s", entry_id)

    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(config_entry, "sensor")]
        )
    )

    # Remove options_update_listener.
    hass.data[DOMAIN][INIT_STATE][UNSUB_OPTIONS_UPDATE_LISTENER][entry_id]()

    # Remove config entry from the domain.
    if unload_ok:
        hass.data[DOMAIN][INIT_STATE][CHARGERS_API].pop(entry_id)

    return unload_ok


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up Go-eCharger platforms and services."""

    _LOGGER.debug("Setting up the Go-eCharger integration")

    charger = ChargerController(hass)

    # expose services for other integrations
    hass.services.async_register(DOMAIN, "start_charging", charger.start_charging)
    hass.services.async_register(DOMAIN, "stop_charging", charger.stop_charging)
    hass.services.async_register(
        DOMAIN, "change_charging_power", charger.change_charging_power
    )
    hass.services.async_register(DOMAIN, "set_phase", charger.set_phase)
    hass.services.async_register(
        DOMAIN, "set_authentication", charger.set_authentication
    )

    scan_interval = DEFAULT_UPDATE_INTERVAL
    chargers_api = _setup_apis(config, hass)

    hass.data[DOMAIN][INIT_STATE] = {
        CHARGERS_API: chargers_api,
        UNSUB_OPTIONS_UPDATE_LISTENER: {},
    }

    charger_names = list(
        map(
            lambda charger: charger[0][CONF_NAME], config[DOMAIN].get(CONF_CHARGERS, [])
        )
    )

    for charger_name in charger_names:
        await _setup_coordinator(
            StateFetcher,
            scan_interval,
            f"{charger_name}_coordinator",
            hass,
        ).async_refresh()

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

    _LOGGER.debug("Setup for the Go-eCharger integration completed")

    return True
