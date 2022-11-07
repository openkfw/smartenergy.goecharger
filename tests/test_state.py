"""Test Go-eCharger state management."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.go_echarger import async_setup
from custom_components.go_echarger.const import (
    DOMAIN,
    ENABLED,
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
    CHARGER_ACCESS: True,
    CHARGER_FORCE_CHARGING: "off",
}
INIT_STATE_NOT_CONNECTED = dict(
    INIT_STATE,
    **{CHARGER_FORCE_CHARGING: "on", "car_status": "Charger ready, no car connected"},
)
INIT_STATE_FULLY_CHARGED = dict(
    INIT_STATE,
    **{
        CHARGER_FORCE_CHARGING: "on",
        "car_status": "Charging finished, car can be disconnected",
    },
)
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
async def test_charge_if_allowed(hass: HomeAssistant) -> None:
    """Test if charging is enabled if car is in the correct state and charging is enabled."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    assert hass.data[DOMAIN][coordinator_name].data[charger_name][ENABLED] is True
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )

    # force state refresh to trigger charging logic
    await hass.data[DOMAIN][coordinator_name].async_refresh()
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "on"
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE_NOT_CONNECTED,
        )
    ),
)
async def test_not_charge_if_not_connected(hass: HomeAssistant) -> None:
    """Test if charging is disabled if car not connected."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "on"
    )

    # force state refresh to trigger charging logic
    await hass.data[DOMAIN][coordinator_name].async_refresh()
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE_FULLY_CHARGED,
        )
    ),
)
async def test_not_charge_if_fully_charged(hass: HomeAssistant) -> None:
    """Test if charging is disabled if car is fully charged."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "on"
    )

    # force state refresh to trigger charging logic
    await hass.data[DOMAIN][coordinator_name].async_refresh()
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )
