"""Test Go-eCharger state management."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.go_echarger import async_setup
from custom_components.go_echarger.const import (
    DOMAIN,
    ENABLED,
    CHARGER_FORCE_CHARGING,
    CONF_CHARGERS,
)
from .mock_api import mocked_api_requests

INIT_STATE_NOT_CONNECTED = dict(
    json.loads(load_fixture("init_state.json")),
    **{CHARGER_FORCE_CHARGING: "on", "car_status": "Charger ready, no car connected"},
)
GO_E_CHARGER_MOCK_REFERENCE = "custom_components.go_echarger.state.GoeChargerApi"
CHARGER_1: dict = json.loads(load_fixture("charger.json"))[0]


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=json.loads(load_fixture("init_state.json")),
        )
    ),
)
async def test_charge_if_allowed(hass: HomeAssistantType) -> None:
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
async def test_not_charge_if_not_connected(hass: HomeAssistantType) -> None:
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
