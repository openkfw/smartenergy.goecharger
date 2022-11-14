"""Sensor platform configuration for go-e Charger Cloud"""

import logging
import numbers
from abc import ABC, abstractmethod
from typing import Callable, Literal

from homeassistant.components.sensor import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    STATE_CLASS_TOTAL,
    SensorEntity,
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)

from .const import (
    CONF_CHARGERS,
    DOMAIN,
    MANUFACTURER,
    CAR_STATUS,
    CHARGING_ALLOWED,
    CHARGER_MAX_CURRENT,
    ENERGY_SINCE_CAR_CONNECTED,
    ENERGY_TOTAL,
    PHASE_SWITCH_MODE,
    PHASES_NUMBER_CONNECTED,
)

MINUTE_IN_MS: Literal[60000] = 60_000

# Reference: https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics
AMPERE: Literal["A"] = "A"
VOLT: Literal["V"] = "V"
POWER_WATT: Literal["W"] = "W"
K_WATT_HOUR: Literal["kWh"] = "kWh"
PERCENT: Literal["%"] = "%"
TIME_MINUTES: Literal["min"] = "min"

_LOGGER: logging.Logger = logging.getLogger(__name__)

CHARGER_SENSORS_CONFIG: dict = {
    "sensors": [
        CAR_STATUS,
        CHARGER_MAX_CURRENT,
        CHARGING_ALLOWED,
        ENERGY_SINCE_CAR_CONNECTED,
        ENERGY_TOTAL,
        PHASE_SWITCH_MODE,
        PHASES_NUMBER_CONNECTED,
        "name",
    ],
    "units": {
        CAR_STATUS: {"unit": "", "name": "Car charging status"},
        CHARGING_ALLOWED: {"unit": "", "name": "Car charging allowed"},
        CHARGER_MAX_CURRENT: {"unit": AMPERE, "name": "Current charging speed (max)"},
        ENERGY_SINCE_CAR_CONNECTED: {
            "unit": K_WATT_HOUR,
            "name": "Energy since car connected",
        },
        ENERGY_TOTAL: {"unit": K_WATT_HOUR, "name": "Energy total"},
        PHASE_SWITCH_MODE: {"unit": "", "name": "Phase switch mode"},
        PHASES_NUMBER_CONNECTED: {"unit": "", "name": "Number of connected phases"},
        "name": {"unit": "", "name": "Charger name"},
    },
    "state_classes": {
        CHARGER_MAX_CURRENT: STATE_CLASS_TOTAL,
        ENERGY_SINCE_CAR_CONNECTED: K_WATT_HOUR,
        ENERGY_TOTAL: K_WATT_HOUR,
    },
    "device_classes": {
        CHARGER_MAX_CURRENT: DEVICE_CLASS_CURRENT,
        ENERGY_SINCE_CAR_CONNECTED: DEVICE_CLASS_ENERGY,
        ENERGY_TOTAL: DEVICE_CLASS_ENERGY,
        CHARGING_ALLOWED: "go_echarger__allow_charging",
        PHASE_SWITCH_MODE: "go_echarger__phase_switch_mode",
    },
}


class BaseSensor(ABC):
    """Representation of a Base sensor."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        coordinator,
        entity_id,
        device_id,
        name,
        attribute,
        unit,
        state_class,
        device_class,
    ) -> None:
        """Initialize the Base sensor."""

        super().__init__(coordinator)
        self._device_id = device_id
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self._attr_state_class = state_class
        self._attr_device_class = device_class

    @property
    @abstractmethod
    def device_info(self) -> None:
        """Return the info about the device."""

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique_id of the sensor."""
        return f"{self._device_id}_{self._attribute}"

    @property
    @abstractmethod
    def state(self) -> None:
        """Return the state of the sensor."""

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit


class ChargerSensor(BaseSensor, CoordinatorEntity, SensorEntity):
    """Representation of a sensor for the go-e Charger Cloud."""

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_id,
            "manufacturer": MANUFACTURER,
            "model": "",
        }

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        attr_value = self.coordinator.data[self._device_id][self._attribute]

        # if charging is not allowed, show current as 0
        if (
            self._attribute == CHARGER_MAX_CURRENT
            and self.coordinator.data[self._device_id][CHARGING_ALLOWED] == "off"
        ):
            return 0

        # convert Wh to kWh and round to 2 decimal positions
        if self._unit == K_WATT_HOUR and isinstance(attr_value, numbers.Number):
            attr_value = round(attr_value / 1000, 2)

        # if attribute is a number and larger than 0, convert it to minutes
        if (
            self.state_class == TIME_MINUTES
            and isinstance(attr_value, numbers.Number)
            and attr_value > 0
        ):
            return round(attr_value / MINUTE_IN_MS, 2)

        return attr_value


def _setup_sensors(
    hass: HomeAssistantType,
    sensor_ids: list,
    sensors_config: dict,
    sensor_class: type,
    coordinator_name: str,
) -> list:
    entities = []

    for sensor_id in sensor_ids:
        sensors = []
        _LOGGER.debug("Creating sensors for the go_echarger=%s", sensor_id)

        for sensor in sensors_config.get("sensors"):
            _LOGGER.debug("Adding sensor=%s for the go_echarger=%s", sensor, sensor_id)

            sensor_unit = (
                sensors_config.get("units").get(sensor).get("unit")
                if sensors_config.get("units").get(sensor)
                else ""
            )
            sensor_name = (
                sensors_config.get("units").get(sensor).get("name")
                if sensors_config.get("units").get(sensor)
                else sensor
            )
            sensor_state_class = (
                sensors_config.get("state_classes")[sensor]
                if sensor in sensors_config.get("state_classes")
                else ""
            )
            sensor_device_class = (
                sensors_config.get("device_classes")[sensor]
                if sensor in sensors_config.get("device_classes")
                else ""
            )

            sensors.append(
                sensor_class(
                    hass.data[DOMAIN][coordinator_name],
                    f"{SENSOR_DOMAIN}.{DOMAIN}_{sensor_id}_{sensor}",
                    sensor_id,
                    sensor_name,
                    sensor,
                    sensor_unit,
                    sensor_state_class,
                    sensor_device_class,
                )
            )

        entities.extend(sensors)

    return entities


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: dict,
    async_add_entities: Callable,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-e Charger Cloud sensor for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        _setup_sensors(
            hass,
            [entry_id],
            CHARGER_SENSORS_CONFIG,
            ChargerSensor,
            f"{entry_id}_coordinator",
        ),
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up go-e Charger Cloud Sensor platform."""
    _LOGGER.debug("Setting up the go-e Charger Cloud sensor platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    for charger_name in discovery_info[CONF_CHARGERS]:
        async_add_entities(
            _setup_sensors(
                hass,
                [charger_name],
                CHARGER_SENSORS_CONFIG,
                ChargerSensor,
                f"{charger_name}_coordinator",
            )
        )
