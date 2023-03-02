"""Test go-e Charger Cloud select inputs."""

import json
from functools import partial
from unittest.mock import Mock, patch

from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.smartenergy_goecharger import async_setup, async_setup_entry
from custom_components.smartenergy_goecharger.const import (
    CONF_CHARGERS,
    DOMAIN,
    PHASE_SWITCH_MODE,
)

from .mock_api import mocked_api_requests

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
async def test_select_input_set_phase(hass: HomeAssistant) -> None:
    """Test if setting of the set phase select input works."""
    charger_name = CHARGER_1[CONF_NAME]
    coordinator_name = f"{charger_name}_coordinator"
    assert await async_setup(hass, {DOMAIN: {CONF_CHARGERS: [[CHARGER_1]]}})
    await hass.async_block_till_done()

    # default value is 1
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][PHASE_SWITCH_MODE] == 1
    )

    # change and expected value is 2
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: f"{SELECT_DOMAIN}.{DOMAIN}_{charger_name}_{PHASE_SWITCH_MODE}",
            ATTR_OPTION: 2,
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][PHASE_SWITCH_MODE] == 2
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
async def test_select_input_set_phase_config_entry(
    hass: HomeAssistant,
) -> None:
    """Test if setting of the set phase select input works - configured via the config entry."""
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

    # default value is 1
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][PHASE_SWITCH_MODE] == 1
    )

    # change and expected value is 2
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: f"{SELECT_DOMAIN}.{DOMAIN}_{charger_name}_{PHASE_SWITCH_MODE}",
            ATTR_OPTION: 2,
        },
        blocking=True,
    )
    assert (
        hass.data[DOMAIN][coordinator_name].data[charger_name][PHASE_SWITCH_MODE] == 2
    )
