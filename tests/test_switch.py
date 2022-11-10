"""Test Go-eCharger switch inputs."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.components.switch import (
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    DOMAIN as SWITCH_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.go_echarger import async_setup
from custom_components.go_echarger.const import (
    DOMAIN,
    CHARGER_FORCE_CHARGING,
    CONF_CHARGERS,
    CAR_STATUS,
    CHARGING_ALLOWED,
)
from .mock_api import mocked_api_requests

INIT_STATE_NOT_CONNECTED = dict(
    json.loads(load_fixture("init_state.json")),
    **{CAR_STATUS: "Charger ready, no car connected", CHARGER_FORCE_CHARGING: "off"},
)
INIT_STATE_NOT_ALLOWED = dict(
    json.loads(load_fixture("init_state.json")),
    **{CHARGING_ALLOWED: "off", CHARGER_FORCE_CHARGING: "off"},
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
async def test_switch_charging_enable_disable(hass: HomeAssistantType) -> None:
    """Test if charging switch can be enabled/disabled."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # switch should be enabled by default
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "on"
    )

    # disable the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_FORCE_CHARGING}"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )

    # enable the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_FORCE_CHARGING}"
        },
        blocking=True,
    )
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
async def test_switch_charging_not_connected(hass: HomeAssistantType) -> None:
    """Test if charging won't be enabled if car not connected."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # switch should be disabled by default
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )

    # enable shouldn't work as car is not connected the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_FORCE_CHARGING}"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE_NOT_ALLOWED,
        )
    ),
)
async def test_switch_charging_not_allowed(hass: HomeAssistantType) -> None:
    """Test if charging won't be enabled if not allowed."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # switch should be disabled by default
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )

    # enable shouldn't work as charging is not allowed at all
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: f"{SWITCH_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_FORCE_CHARGING}"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )
