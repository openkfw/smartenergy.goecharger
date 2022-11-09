"""Switch platform configuration for Go-eCharger"""

import logging
from typing import Callable
from abc import ABC, abstractmethod

from homeassistant.components.switch import SwitchEntity, DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)

from .const import DOMAIN, CONF_CHARGERS, MANUFACTURER, ENABLED
from .controller import ChargerController

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BaseSwitch(ABC):
    """Representation of a Base switch."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        coordinator,
        entity_id,
        name,
        attribute,
        device_id,
        hass,
    ) -> None:
        """Initialize the go-eCharger switch."""
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._device_id = device_id
        self._state = None
        self._charger_controller = ChargerController(hass)

    @property
    def device_info(self) -> dict:
        """Return the info about the device."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_id,
            "manufacturer": MANUFACTURER,
            "model": "",
        }

    @abstractmethod
    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""

    @abstractmethod
    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the switch."""
        return f"{self._device_id}_{self._attribute}"

    @property
    @abstractmethod
    def is_on(self) -> str | int:
        """Return the state of the switch."""


class EnableDisableSwitch(BaseSwitch, CoordinatorEntity, SwitchEntity):
    """Representation of a switch for enabling/disabling of charging."""

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.coordinator.data[self._device_id][self._attribute] = True
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        self.coordinator.data[self._device_id][self._attribute] = False
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> str | int:
        """Return the state of the switch."""
        return self.coordinator.data[self._device_id][self._attribute]


def _create_enable_disable_switch(
    hass: HomeAssistantType, charger_name: str
) -> EnableDisableSwitch:
    """
    Create a switch for authentication attribute. This will toggle access control  to the car.
    """
    return EnableDisableSwitch(
        hass.data[DOMAIN][f"{charger_name}_coordinator"],
        f"{SWITCH_DOMAIN}.{DOMAIN}_{charger_name}_{ENABLED}",
        "Enable/disable charging",
        ENABLED,
        charger_name,
        hass,
    )


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: dict,
    async_add_entities: Callable,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-eCharger switch for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        [_create_enable_disable_switch(hass, entry_id)],
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    _config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up go-eCharger Switch platform."""
    _LOGGER.debug("Setting up the go-eCharger switch platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    for charger_name in discovery_info[CONF_CHARGERS]:
        async_add_entities([_create_enable_disable_switch(hass, charger_name)])
