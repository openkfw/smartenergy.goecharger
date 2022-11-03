"""Test integration_blueprint switch."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.go_echarger import async_setup
from custom_components.go_echarger.const import (
    DOMAIN,
    ENABLED,
    CONF_CHARGERS,
)
from .mock_api import mocked_api_requests

INIT_STATE = {
    "car_status": None,
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
async def test_switch_enable_disable(hass: HomeAssistant) -> None:
    """Test if charging switch can be enabled/disabled."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # switch should be enabled by default
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][ENABLED] is True

    # disable the switch
    await hass.services.async_call(
        "switch",
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: f"switch.{DOMAIN}_{charger_name}_{ENABLED}"},
        blocking=True,
    )
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][ENABLED] is False

    # enable the switch
    await hass.services.async_call(
        "switch",
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: f"switch.{DOMAIN}_{charger_name}_{ENABLED}"},
        blocking=True,
    )
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][ENABLED] is True
