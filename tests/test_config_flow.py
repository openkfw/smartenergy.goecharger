"""Test the Go-eCharger config flow and options flow."""

import json

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from custom_components.go_echarger.const import DOMAIN


CHARGER_1: dict = json.loads(load_fixture("charger.json"))[0]
CHARGER_2: dict = json.loads(load_fixture("charger.json"))[0]
CHARGER_3: dict = json.loads(load_fixture("charger.json"))[0]


async def test_config_flow_init(hass: HomeAssistant) -> None:
    """Test we can configure the integration via config flow."""
    result_init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result_init["type"] == RESULT_TYPE_FORM
    assert result_init["errors"] is None

    result_configure = await hass.config_entries.flow.async_configure(
        result_init["flow_id"],
        CHARGER_1,
    )
    await hass.async_block_till_done()

    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == "charger1"
    assert result_configure["data"] == CHARGER_1


async def test_options_flow_init(hass) -> None:
    """Test we can configure the integration via options flow."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="added_charger",
        data=CHARGER_2,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result_init = await hass.config_entries.options.async_init(config_entry.entry_id)
    result_configure = await hass.config_entries.options.async_configure(
        result_init["flow_id"],
        user_input=CHARGER_3,
    )
    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == ""
    assert result_configure["result"] is True
    assert result_configure["data"] == CHARGER_3
