"""Support for Go-eCharger custom buttons."""

from __future__ import annotations
import logging
from typing import Callable

from dataclasses import dataclass
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
    DOMAIN as BUTTON_DOMAIN,
)
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)

from .const import DOMAIN, CONF_CHARGERS
from .controller import ChargerController

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class BaseButtonDescription(ButtonEntityDescription):
    """Class to describe a Base button."""

    press_args = None


# pylint: disable=too-few-public-methods
class BaseDescriptiveEntity:
    """Representation of a Base device entity based on a description."""

    def __init__(
        self,
        device_id,
        description,
        hass,
    ) -> None:
        """Initialize the device."""
        super().__init__()
        self.entity_description = description
        self.entity_id = description.key
        self._attr_unique_id = description.key
        self._device_id = device_id
        self._charger_controller = ChargerController(hass)


class AuthButton(BaseDescriptiveEntity, ButtonEntity):
    """Representation of an Auth Button."""

    entity_description = None

    async def async_press(self) -> None:
        """Handle the button press. Authenticates the user against the wallbox"""

        await self._charger_controller.set_authentication(
            {"data": {"device_name": self._device_id, "status": 0}}
        )


def _create_buttons(hass: HomeAssistantType, chargers: dict) -> list[AuthButton]:
    button_entities = []

    for charger_name in chargers:
        button_entities.append(
            AuthButton(
                charger_name,
                BaseButtonDescription(
                    key=f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_authentication",
                    name="Authenticate",
                    icon="mdi:security",
                ),
                hass,
            )
        )

    return button_entities


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: dict,
    async_add_entities: Callable,
) -> None:
    """Setup buttons from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-eCharger button for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        _create_buttons(hass, [entry_id]),
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up go-eCharger Button platform."""
    _LOGGER.debug("Setting up the go-eCharger button platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    async_add_entities(_create_buttons(hass, discovery_info[CONF_CHARGERS]))
