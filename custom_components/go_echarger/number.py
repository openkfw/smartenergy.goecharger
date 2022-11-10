"""Support for Go-eCharger custom number inputs."""

from __future__ import annotations
import logging
from typing import Callable

from dataclasses import dataclass
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    DOMAIN as NUMBER_DOMAIN,
)
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_CHARGERS,
    MIN_CHARGING_CURRENT_LIMIT,
    MAX_CHARGING_CURRENT_LIMIT,
)
from .controller import ChargerController

_LOGGER: logging.Logger = logging.getLogger(__name__)

NUMBER_INPUTS = [
    {
        "id": "charger_max_current",
        "name": "Set charging speed",
        "icon": "mdi:current-ac",
    }
]


@dataclass
class BaseNumberDescription(NumberEntityDescription):
    """Class to describe a Base number input."""

    press_args = None


# pylint: disable=too-few-public-methods
class BaseDescriptiveEntity:
    """Representation of a Base device entity based on a description."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        hass,
        coordinator,
        device_id,
        description,
        input_id,
        input_props,
    ) -> None:
        """Initialize the device."""

        super().__init__(coordinator)
        self.entity_description = description
        self.entity_id = description.key
        self._attr_unique_id = description.key
        self._device_id = device_id
        self._charger_controller = ChargerController(hass)
        self._attribute = input_id
        self._min = input_props["min"]
        self._max = input_props["max"]
        self._step = input_props["step"]


class CurrentInputNumber(BaseDescriptiveEntity, CoordinatorEntity, NumberEntity):
    """Representation of the current number input."""

    entity_description: BaseNumberDescription = None

    @property
    def native_max_value(self) -> float:
        """Return the maximum available current."""
        return self._max

    @property
    def native_min_value(self) -> float:
        """Return the minimum available current."""
        return self._min

    @property
    def native_step(self) -> float:
        return self._step

    @property
    def native_value(self) -> float | None:
        """Return the value of the entity."""
        return self.coordinator.data[self._device_id][self._attribute]

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        await self._charger_controller.change_charging_power(
            {"data": {"device_name": self._device_id, "charging_power": int(value)}}
        )


def _create_input_numbers(
    hass: HomeAssistantType, chargers: list[str]
) -> list[CurrentInputNumber]:
    """
    Create input number sliders for defined entities.
    """
    number_entities = []

    for charger_name in chargers:
        min_limit = hass.data[DOMAIN][f"{charger_name}_coordinator"].data[charger_name][
            MIN_CHARGING_CURRENT_LIMIT
        ]
        max_limit = hass.data[DOMAIN][f"{charger_name}_coordinator"].data[charger_name][
            MAX_CHARGING_CURRENT_LIMIT
        ]

        if min_limit >= max_limit:
            _LOGGER.error(
                "Min limit is greater than/equal to the max limit, can't configure the number input"
            )
        else:
            for number_input in NUMBER_INPUTS:
                number_entities.append(
                    CurrentInputNumber(
                        hass,
                        hass.data[DOMAIN][f"{charger_name}_coordinator"],
                        charger_name,
                        BaseNumberDescription(
                            key=f"{NUMBER_DOMAIN}.{DOMAIN}_{charger_name}_{number_input['id']}",
                            name=number_input["name"],
                            icon=number_input["icon"],
                        ),
                        number_input["id"],
                        {
                            "min": min_limit,
                            "max": max_limit,
                            "step": 1,
                        },
                    )
                )

    return number_entities


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: dict,
    async_add_entities: Callable,
) -> None:
    """Setup number inputs from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-eCharger button for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        _create_input_numbers(hass, [entry_id]),
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up go-eCharger number platform."""
    _LOGGER.debug("Setting up the go-eCharger number platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    async_add_entities(_create_input_numbers(hass, discovery_info[CONF_CHARGERS]))