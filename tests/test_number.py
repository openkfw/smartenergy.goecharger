"""Test go-e Charger Cloud number inputs."""

import json
from functools import partial
from unittest.mock import Mock, patch

from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.smartenergy_goecharger import async_setup, async_setup_entry
from custom_components.smartenergy_goecharger.const import (
    CHARGER_MAX_CURRENT,
    CONF_CHARGERS,
    DOMAIN,
    MAX_CHARGING_CURRENT_LIMIT,
    MIN_CHARGING_CURRENT_LIMIT,
)

from .mock_api import mocked_api_requests

INIT_STATE_WRONG_LIMITS = dict(
    json.loads(load_fixture("init_state.json")),
    **{MAX_CHARGING_CURRENT_LIMIT: 4, MIN_CHARGING_CURRENT_LIMIT: 5},
)

GO_E_CHARGER_MOCK_REFERENCE = f"custom_components.{DOMAIN}.state.GoeChargerApi"
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
async def test_number_input_max_current_change(hass: HomeAssistant) -> None:
    """Test if changing of the max current number input works."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # default value is 2
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 2
    )

    # change and expected value is 4
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: f"{NUMBER_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_MAX_CURRENT}",
            ATTR_VALUE: 4,
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 4
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(
        side_effect=partial(
            mocked_api_requests,
            data=INIT_STATE_WRONG_LIMITS,
        )
    ),
)
async def test_number_input_max_current_change_wrong_limits(
    hass: HomeAssistant,
) -> None:
    """Test if changing of the max current number doesn't work if min greater than Max."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # default value is 2
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 2
    )
    # number input shouldn't even be created
    assert (
        f"{NUMBER_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_MAX_CURRENT}"
        not in hass.states.async_entity_ids()
    )

    # therefore, change this change/call shouldn't do anything
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: f"{NUMBER_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_MAX_CURRENT}",
            ATTR_VALUE: 4,
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 2
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
async def test_number_input_max_current_change_config_entry(
    hass: HomeAssistant,
) -> None:
    """Test if changing of the max current number input works - configured via the config entry."""
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

    # default value is 2
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 2
    )

    # change and expected value is 4
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: f"{NUMBER_DOMAIN}.{DOMAIN}_{charger_name}_{CHARGER_MAX_CURRENT}",
            ATTR_VALUE: 4,
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][CHARGER_MAX_CURRENT] == 4
    )
