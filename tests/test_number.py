"""Test Go-eCharger button inputs."""

import json
from functools import partial
from unittest.mock import patch, Mock

from homeassistant.components.number import (
    ATTR_VALUE,
    SERVICE_SET_VALUE,
    DOMAIN as NUMBER_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.go_echarger import async_setup, async_setup_entry
from custom_components.go_echarger.const import (
    DOMAIN,
    CONF_CHARGERS,
    CHARGER_MAX_CURRENT,
)
from .mock_api import mocked_api_requests

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
async def test_number_input_max_current_change(hass: HomeAssistantType) -> None:
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
            data=json.loads(load_fixture("init_state.json")),
        )
    ),
)
async def test_number_input_max_current_change_config_entry(
    hass: HomeAssistantType,
) -> None:
    """Test if changing of the max current number input works
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
