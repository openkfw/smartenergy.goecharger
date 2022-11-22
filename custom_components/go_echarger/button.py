"""Support for go-e Charger Cloud custom buttons."""

from __future__ import annotations
import logging
from typing import Callable

from dataclasses import dataclass
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
    DOMAIN as BUTTON_DOMAIN,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)

from .const import (
    DOMAIN,
    CONF_CHARGERS,
    CAR_STATUS,
    STATUS,
    ONLINE,
    OFFLINE,
    WALLBOX_CONTROL,
    CarStatus,
)
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
        hass,
        coordinator,
        device_id,
        description,
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)
        self.entity_description = description
        self.entity_id = description.key
        self._attr_unique_id = description.key
        self._device_id = device_id
        self._charger_controller = ChargerController(hass)


class WallboxControlButton(BaseDescriptiveEntity, CoordinatorEntity, ButtonEntity):
    """Representation of a Charge Button."""

    entity_description: BaseButtonDescription = None

    async def async_press(self) -> None:
        """Handle the button press. Start/stop charging or authenticate the user."""

        data = self.coordinator.data[self._device_id]

        if data[STATUS] == OFFLINE:
            return False

        match data[CAR_STATUS]:
            case CarStatus.CAR_CHARGING:
                # car status is 2 - stop charging
                await self._charger_controller.stop_charging(
                    {"data": {"device_name": self._device_id}}
                )
            case CarStatus.CAR_CONNECTED_AUTH_REQUIRED:
                # car status is 3 - authenticate
                await self._charger_controller.set_transaction(
                    {"data": {"device_name": self._device_id, "status": 0}}
                )
            case CarStatus.CHARGING_FINISHED_DISCONNECT:
                # car status is 4 - start charging
                await self._charger_controller.start_charging(
                    {"data": {"device_name": self._device_id}}
                )
            case _:
                # car status is 1 - do nothing
                pass

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        data = self.coordinator.data[self._device_id]

        if data[STATUS] == OFFLINE:
            return "Wallbox is offline"

        match data[CAR_STATUS]:
            case CarStatus.CAR_CHARGING:
                # car status is 2 - stop charging
                return "Stop charging"
            case CarStatus.CAR_CONNECTED_AUTH_REQUIRED:
                # car status is 3 - authenticate
                return "Authenticate car"
            case CarStatus.CHARGING_FINISHED_DISCONNECT:
                # car status is 4 - start charging
                return "Start charging"
            case _:
                # car status is 1 - do nothing
                return "Please connect car"

    @property
    def available(self) -> bool:
        """Make the button (un)available based on the status."""

        data = self.coordinator.data[self._device_id]

        return data[STATUS] == ONLINE


def _create_buttons(
    hass: HomeAssistantType, chargers: list[str]
) -> list[WallboxControlButton]:
    """
    Create input buttons for authentication.
    """
    button_entities = []

    for charger_name in chargers:
        button_entities.append(
            WallboxControlButton(
                hass,
                hass.data[DOMAIN][f"{charger_name}_coordinator"],
                charger_name,
                BaseButtonDescription(
                    key=f"{BUTTON_DOMAIN}.{DOMAIN}_{charger_name}_{WALLBOX_CONTROL}",
                    name="Wallbox control",
                    icon="mdi:battery-charging",
                ),
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
    _LOGGER.debug("Setting up the go-e Charger Cloud button for=%s", entry_id)

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
    """Set up go-e Charger Cloud Button platform."""
    _LOGGER.debug("Setting up the go-e Charger Cloud button platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    async_add_entities(_create_buttons(hass, discovery_info[CONF_CHARGERS]))
