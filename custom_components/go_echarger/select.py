"""Support for Go-eCharger custom select inputs."""

from __future__ import annotations
import logging
from typing import Callable

from dataclasses import dataclass
from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
    DOMAIN as SELECT_DOMAIN,
)
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_CHARGERS, PHASE_SWITCH_MODE
from .controller import ChargerController

_LOGGER: logging.Logger = logging.getLogger(__name__)

SELECT_INPUTS = [
    {
        "id": PHASE_SWITCH_MODE,
        "name": "Set phase mode",
        "icon": "mdi:eye",
        "options": ["0", "1", "2"],
    }
]


@dataclass
class BaseSelectDescription(SelectEntityDescription):
    """Class to describe a Base select input."""

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
        device_class,
        input_id,
        input_options,
        input_initial_option,
    ) -> None:
        """Initialize the device."""

        super().__init__(coordinator)
        self.entity_description = description
        self.entity_id = description.key
        self._attr_unique_id = description.key
        self._device_id = device_id
        self._charger_controller = ChargerController(hass)
        self._attribute = input_id
        self._attr_current_option = input_initial_option
        self._attr_options = input_options
        self._attr_device_class = device_class


class PhaseSelectInput(BaseDescriptiveEntity, CoordinatorEntity, SelectEntity):
    """Representation of the phase mode select input."""

    entity_description: BaseSelectDescription = None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._charger_controller.set_phase(
            {"data": {"device_name": self._device_id, "phase": int(option)}}
        )

    @property
    def current_option(self) -> str | None:
        """Return the state of the entity."""
        return str(self.coordinator.data[self._device_id][self._attribute])


def _create_select_inputs(
    hass: HomeAssistantType, chargers: list[str]
) -> list[PhaseSelectInput]:
    """
    Create select inputs for defined entities.
    """
    select_entities = []

    for charger_name in chargers:
        for select_input in SELECT_INPUTS:
            select_entities.append(
                PhaseSelectInput(
                    hass,
                    hass.data[DOMAIN][f"{charger_name}_coordinator"],
                    charger_name,
                    BaseSelectDescription(
                        key=f"{SELECT_DOMAIN}.{DOMAIN}_{charger_name}_{select_input['id']}",
                        name=select_input["name"],
                        icon=select_input["icon"],
                    ),
                    "go_echarger__phase_switch_mode",
                    select_input["id"],
                    select_input["options"],
                    str(
                        hass.data[DOMAIN][f"{charger_name}_coordinator"].data[
                            charger_name
                        ][PHASE_SWITCH_MODE]
                    ),
                )
            )

    return select_entities


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: dict,
    async_add_entities: Callable,
) -> None:
    """Setup select inputs from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-eCharger button for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        _create_select_inputs(hass, [entry_id]),
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up go-eCharger select platform."""
    _LOGGER.debug("Setting up the go-eCharger select platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    async_add_entities(_create_select_inputs(hass, discovery_info[CONF_CHARGERS]))
