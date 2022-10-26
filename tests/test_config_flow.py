"""Test the Go-eCharger config flow and options flow."""

from http.client import BAD_REQUEST, OK
import json
from unittest.mock import patch, Mock

import pytest

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from custom_components.go_echarger.const import DOMAIN

GO_E_CHARGER_MOCK_REFERENCE = "custom_components.go_echarger.config_flow.GoeChargerApi"

CHARGER_1: dict = json.loads(load_fixture("charger.json"))[0]
CHARGER_2: dict = json.loads(load_fixture("charger.json"))[1]
CHARGER_3: dict = json.loads(load_fixture("charger.json"))[2]
CHARGER_INVALID_INTERVAL_MIN: dict = json.loads(load_fixture("charger.json"))[3]
CHARGER_INVALID_INTERVAL_MAX: dict = json.loads(load_fixture("charger.json"))[4]
CHARGER_INVALID_HOST_PREFIX: dict = json.loads(load_fixture("charger.json"))[5]
CHARGER_INVALID_HOST_SUFFIX: dict = json.loads(load_fixture("charger.json"))[6]
CHARGER_AUTH_FAILED: dict = json.loads(load_fixture("charger.json"))[7]


# pylint: disable=unused-argument
def mocked_api_requests(*args, **kwargs) -> dict | int:
    """Module handling mocked API requests"""

    class MockResponse:
        """Class handling mocked API responses"""

        def __init__(self, json_data, status_code) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def request_status(self) -> dict:
            """Return data as a JSON"""
            return self.json_data

    if args[0] in ["http://1.1.1.1", "http://1.1.1.2"]:
        return MockResponse({}, OK)

    return BAD_REQUEST


async def _initialize_and_assert_flow(hass: HomeAssistant) -> FlowResult:
    result_init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result_init["type"] == RESULT_TYPE_FORM
    assert result_init["errors"] is None

    return result_init


async def _initialize_and_assert_options(hass: HomeAssistant, data: dict) -> FlowResult:
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="added_charger",
        data=data,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result_init = await hass.config_entries.options.async_init(config_entry.entry_id)

    return result_init


async def _assert_invalid_host(flow_id: str, data: dict, configure_fn) -> None:
    """Test an error is created when host is invalid."""
    # wrong protocol
    result_configure = await configure_fn(
        flow_id,
        data,
    )

    assert result_configure["errors"] == {"base": "invalid_host"}


async def _assert_invalid_scan_interval(
    flow_id: str,
    data: dict,
    configure_fn,
    err_msg: str,
) -> None:
    """Test an error is created when scan interval is invalid."""
    with pytest.raises(Exception) as exception_info:
        await configure_fn(
            flow_id,
            data,
        )
    assert str(exception_info.value) == err_msg


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(side_effect=mocked_api_requests),
)
async def _assert_invalid_auth(flow_id: str, data: dict, configure_fn) -> None:
    """Test an error is created when host and token failed to authenticate."""
    # invalid auth credentials
    result_configure = await configure_fn(
        flow_id,
        data,
    )
    assert result_configure["errors"] == {"base": "invalid_auth"}


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(side_effect=mocked_api_requests),
)
async def test_config_flow_init(hass: HomeAssistant) -> None:
    """Test we can configure the integration via config flow."""
    result_init = await _initialize_and_assert_flow(hass)
    result_configure = await hass.config_entries.flow.async_configure(
        result_init["flow_id"],
        CHARGER_1,
    )
    await hass.async_block_till_done()

    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == "charger1"
    assert result_configure["data"] == CHARGER_1


async def test_config_flow_invalid_host(hass: HomeAssistant) -> None:
    """Test an error is created when host is invalid."""
    result_init = await _initialize_and_assert_flow(hass)
    # wrong protocol
    await _assert_invalid_host(
        result_init["flow_id"],
        CHARGER_INVALID_HOST_PREFIX,
        hass.config_entries.flow.async_configure,
    )
    # extra trailing slash
    await _assert_invalid_host(
        result_init["flow_id"],
        CHARGER_INVALID_HOST_SUFFIX,
        hass.config_entries.flow.async_configure,
    )


async def test_config_flow_invalid_scan_interval(hass: HomeAssistant) -> None:
    """Test an error is created when scan interval is invalid."""
    result_init = await _initialize_and_assert_flow(hass)
    # min is 1
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CHARGER_INVALID_INTERVAL_MIN,
        hass.config_entries.flow.async_configure,
        "value must be at least 1 for dictionary value @ data['scan_interval']",
    )
    # max is 60000
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CHARGER_INVALID_INTERVAL_MAX,
        hass.config_entries.flow.async_configure,
        "value must be at most 60000 for dictionary value @ data['scan_interval']",
    )


async def test_config_flow_invalid_auth(hass: HomeAssistant) -> None:
    """Test an error is created when host and token failed to authenticate."""
    result_init = await _initialize_and_assert_flow(hass)
    await _assert_invalid_auth(
        result_init["flow_id"],
        CHARGER_AUTH_FAILED,
        hass.config_entries.flow.async_configure,
    )


@patch(
    GO_E_CHARGER_MOCK_REFERENCE,
    Mock(side_effect=mocked_api_requests),
)
async def test_options_flow_init(hass) -> None:
    """Test we can configure the integration via options flow."""
    result_init = await _initialize_and_assert_options(hass, CHARGER_2)

    result_configure = await hass.config_entries.options.async_configure(
        result_init["flow_id"],
        CHARGER_3,
    )
    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == ""
    assert result_configure["result"] is True
    assert result_configure["data"] == CHARGER_3


async def test_options_flow_invalid_host(hass: HomeAssistant) -> None:
    """Test an error is created when host is invalid."""
    result_init = await _initialize_and_assert_options(hass, CHARGER_2)
    # wrong protocol
    await _assert_invalid_host(
        result_init["flow_id"],
        CHARGER_INVALID_HOST_PREFIX,
        hass.config_entries.options.async_configure,
    )
    # extra trailing slash
    await _assert_invalid_host(
        result_init["flow_id"],
        CHARGER_INVALID_HOST_SUFFIX,
        hass.config_entries.options.async_configure,
    )


async def test_options_flow_invalid_scan_interval(hass: HomeAssistant) -> None:
    """Test an error is created when scan interval is invalid."""
    result_init = await _initialize_and_assert_options(hass, CHARGER_2)
    # min is 1
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CHARGER_INVALID_INTERVAL_MIN,
        hass.config_entries.options.async_configure,
        "value must be at least 1 for dictionary value @ data['scan_interval']",
    )
    # max is 60000
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CHARGER_INVALID_INTERVAL_MAX,
        hass.config_entries.options.async_configure,
        "value must be at most 60000 for dictionary value @ data['scan_interval']",
    )


async def test_options_flow_invalid_auth(hass: HomeAssistant) -> None:
    """Test an error is created when host and token failed to authenticate."""
    result_init = await _initialize_and_assert_options(hass, CHARGER_2)
    await _assert_invalid_auth(
        result_init["flow_id"],
        CHARGER_AUTH_FAILED,
        hass.config_entries.options.async_configure,
    )
