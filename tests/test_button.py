"""Test go-e Charger Cloud button inputs."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.components.button import SERVICE_PRESS, DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.smart_energy_goecharger import async_setup, async_setup_entry
from custom_components.smart_energy_goecharger.const import (
    DOMAIN,
    STATUS,
    CONF_CHARGERS,
    CAR_STATUS,
    CHARGER_FORCE_CHARGING,
    TRANSACTION,
    WALLBOX_CONTROL,
    OFFLINE,
    CarStatus,
)
from .mock_api import mocked_api_requests

GO_E_CHARGER_MOCK_REFERENCE = (
    "custom_components.smart_energy_goecharger.state.GoeChargerApi"
)
CHARGER_1: dict = json.loads(load_fixture("charger.json"))[0]
CHARGER_CAR_STATUS_1 = dict(
    json.loads(load_fixture("init_state.json")),
    **{CAR_STATUS: CarStatus.CHARGER_READY_NO_CAR},
)
CHARGER_CAR_STATUS_3 = dict(
    json.loads(load_fixture("init_state.json")),
    **{CAR_STATUS: CarStatus.CAR_CONNECTED_AUTH_REQUIRED},
)
CHARGER_CAR_STATUS_4 = dict(
    json.loads(load_fixture("init_state.json")),
    **{CAR_STATUS: CarStatus.CHARGING_FINISHED_DISCONNECT},
)


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=json.loads(load_fixture("init_state.json")),
        )
    ),
)
async def test_button_wallbox_charge_stop(hass: HomeAssistantType) -> None:
    """Test if pressing the button stops the charging."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device is in the force state "neutral"
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "neutral"
    )

    # change the force state to "off"
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}"
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
            data=CHARGER_CAR_STATUS_3,
        )
    ),
)
async def test_button_wallbox_auth(hass: HomeAssistantType) -> None:
    """Test if pressing the button enables the device authentication."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device has no transaction by default
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][TRANSACTION] is None

    # change the transaction to "0" to do the authentication
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}"
        },
        blocking=True,
    )
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][TRANSACTION] == 0


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=CHARGER_CAR_STATUS_4,
        )
    ),
)
async def test_button_wallbox_charge_start(hass: HomeAssistantType) -> None:
    """Test if pressing the button starts the charging."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device is in the force state "neutral"
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "neutral"
    )

    # change the force state to "on"
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}"
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
            data=CHARGER_CAR_STATUS_1,
        )
    ),
)
async def test_button_wallbox_disabled(hass: HomeAssistantType) -> None:
    """Test if pressing of the button is disabled when car is not connected."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device is in the force state "neutral" and trx "None"
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "neutral"
    )
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][TRANSACTION] is None

    # button should be disabled
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}"
        },
        blocking=True,
    )

    # therefore expect the same values
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "neutral"
    )
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][TRANSACTION] is None


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data={"success": False, "msg": "Wallbox is offline"},
        )
    ),
)
async def test_button_wallbox_offline(hass: HomeAssistantType) -> None:
    """Test if wallbox is set to the offline mode when wallbox itself is offline."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # device should be in the "offline" mode if wallbox is offline
    assert hass.data[DOMAIN][coordinator_name].data[charger_name][STATUS] == OFFLINE


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=json.loads(load_fixture("init_state.json")),
        )
    ),
)
async def test_button_wallbox_charge_stop_config_entry(hass: HomeAssistantType) -> None:
    """Test if pressing the button stops the charging,
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

    # device is in the force state "neutral"
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "neutral"
    )

    # change the force state to "off"
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data={
            ATTR_ENTITY_ID: f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}"
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_FORCE_CHARGING]
        == "off"
    )
