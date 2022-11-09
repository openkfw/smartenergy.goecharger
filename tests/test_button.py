"""Test Go-eCharger button inputs."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.core import HomeAssistant
from homeassistant.components.button import SERVICE_PRESS, DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.go_echarger import async_setup, async_setup_entry
from custom_components.go_echarger.const import (
    DOMAIN,
    CHARGER_ACCESS,
    CHARGER_FORCE_CHARGING,
    CONF_CHARGERS,
)
from .mock_api import mocked_api_requests

INIT_STATE = {
    "car_status": "Car is charging",
    "serial_number": None,
    "charger_max_current": None,
    "charging_allowed": None,
    "allowed_ampere": None,
    "energy_since_car_connected": None,
    "charging_duration": {"type": 1, "value": 0},
    "min_charging_time": 0,
    "car_consumption": None,
    "rssi_signal_strength": None,
    "energy_total": None,
    "charging_limit": None,
    "phase_switch_mode": None,
    CHARGER_ACCESS: False,
    CHARGER_FORCE_CHARGING: "off",
}
GO_E_CHARGER_MOCK_REFERENCE = "custom_components.go_echarger.state.GoeChargerApi"
CHARGER_1: dict = json.loads(load_fixture("charger.json"))[0]


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE,
        )
    ),
)
async def test_button_auth_enable(hass: HomeAssistant) -> None:
    """Test if pressing the button enables the device authentication."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device is by default not authenticated
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_ACCESS] is False
    )

    # authenticate the device
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_authentication"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_ACCESS] is True
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE,
        )
    ),
)
async def test_button_auth_enable_config_entry(hass: HomeAssistant) -> None:
    """Test if pressing the button enables the device authentication
    if configured via the config entry."""
    charger_name = "test"
    coordinator_name = f"{charger_name}_coordinator"
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="added_charger",
        data=CHARGER_1,
        options=CHARGER_1,
        entry_id=charger_name,
    )
    assert await async_setup(hass, {})
    await hass.async_block_till_done()
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # device is by default not authenticated
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_ACCESS] is False
    )

    # authenticate the device
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_authentication"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_ACCESS] is True
    )
