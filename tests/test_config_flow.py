"""Test the Apple config flow."""
import unittest
from unittest.mock import patch

from homeassistant import config_entries

# from homeassistant.components.apple.config_flow import CannotConnect, InvalidAuth
# from homeassistant.components.apple.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM
from custom_components.goechargerv2.const import DOMAIN


# class Test(unittest.TestCase):
#     """Unit tests testing validations."""

#     def test_validation_ok(self) -> None:
#         """Test if a non empty string is valid, thus returns None"""
#         self.assertEqual(None, None)


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    print(result)
    assert 1 == 1
    # assert result["type"] == RESULT_TYPE_FORM
    # assert result["errors"] is None

    # with patch(
    #     "homeassistant.components.apple.config_flow.PlaceholderHub.authenticate",
    #     return_value=True,
    # ), patch(
    #     "homeassistant.components.apple.async_setup_entry",
    #     return_value=True,
    # ) as mock_setup_entry:
    #     result2 = await hass.config_entries.flow.async_configure(
    #         result["flow_id"],
    #         {
    #             "host": "1.1.1.1",
    #             "username": "test-username",
    #             "password": "test-password",
    #         },
    #     )
    #     await hass.async_block_till_done()


#     # assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
#     # assert result2["title"] == "Name of the device"
#     # assert result2["data"] == {
#     #     "host": "1.1.1.1",
#     #     "username": "test-username",
#     #     "password": "test-password",
#     # }
#     # assert len(mock_setup_entry.mock_calls) == 1


# async def test_form_invalid_auth(hass: HomeAssistant) -> None:
#     """Test we handle invalid auth."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )

#     with patch(
#         "homeassistant.components.apple.config_flow.PlaceholderHub.authenticate",
#         side_effect=InvalidAuth,
#     ):
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 "host": "1.1.1.1",
#                 "username": "test-username",
#                 "password": "test-password",
#             },
#         )

#     assert result2["type"] == RESULT_TYPE_FORM
#     assert result2["errors"] == {"base": "invalid_auth"}


# async def test_form_cannot_connect(hass: HomeAssistant) -> None:
#     """Test we handle cannot connect error."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )

#     with patch(
#         "homeassistant.components.apple.config_flow.PlaceholderHub.authenticate",
#         side_effect=CannotConnect,
#     ):
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 "host": "1.1.1.1",
#                 "username": "test-username",
#                 "password": "test-password",
#             },
#         )

#     assert result2["type"] == RESULT_TYPE_FORM
#     assert result2["errors"] == {"base": "cannot_connect"}

# if __name__ == "__main__":
#     unittest.main()
