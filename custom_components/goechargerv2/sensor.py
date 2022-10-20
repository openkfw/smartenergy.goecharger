"""Sensor platform configuration for Go-eCharger"""

import logging
from abc import ABC, abstractmethod
from typing import Literal

from homeassistant.components.sensor import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    STATE_CLASS_TOTAL,
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CHARGERS, DOMAIN

MINUTE_IN_MS: Literal[60000] = 60_000

# Reference: https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics
AMPERE: Literal["A"] = "A"
VOLT: Literal["V"] = "V"
POWER_WATT: Literal["W"] = "W"
WATT_HOUR: Literal["Wh"] = "Wh"
PERCENT: Literal["%"] = "%"
TIME_MINUTES: Literal["min"] = "min"

_LOGGER: logging.Logger = logging.getLogger(__name__)

CHARGER_SENSORS_CONFIG: dict = {
    "sensors": [
        "car_status",
        "serial_number",
        "charger_max_current",
        "charging_allowed",
        "allowed_ampere",
        "energy_since_car_connected",
        "charging_duration",
        "min_charging_time",
        "car_consumption",
        "rssi_signal_strength",
        "energy_total",
        "charging_limit",
        "phase_switch_mode",
        "name",
    ],
    "units": {
        "car_status": {"unit": "", "name": "Car charging status"},
        "serial_number": {"unit": "", "name": "Serial number"},
        "charging_allowed": {"unit": "", "name": "Car charging allowed"},
        "charger_max_current": {"unit": AMPERE, "name": "Charger Max Current"},
        "allowed_ampere": {"unit": AMPERE, "name": "Amperes allowed to charge"},
        "energy_since_car_connected": {
            "unit": WATT_HOUR,
            "name": "Energy since car connected",
        },
        "charging_duration": {"unit": TIME_MINUTES, "name": "Charging duration"},
        "min_charging_time": {"unit": TIME_MINUTES, "name": "Minimal charging time"},
        "car_consumption": {"unit": "", "name": "Car consumption"},
        "rssi_signal_strength": {"unit": "", "name": "RSSI signal strength"},
        "energy_total": {"unit": WATT_HOUR, "name": "Energy total"},
        "charging_limit": {"unit": WATT_HOUR, "name": "Charging energy limit"},
        "phase_switch_mode": {"unit": "", "name": "Phase switch mode"},
        "name": {"unit": "", "name": "Friendly car name"},
    },
    "state_classes": {
        "charger_max_current": STATE_CLASS_TOTAL,
        "allowed_ampere": AMPERE,
        "energy_since_car_connected": WATT_HOUR,
        "energy_total": WATT_HOUR,
        "charging_limit": WATT_HOUR,
        "charging_duration": TIME_MINUTES,
        "min_charging_time": TIME_MINUTES,
    },
    "device_classes": {
        "charger_max_current": DEVICE_CLASS_CURRENT,
        "allowed_ampere": DEVICE_CLASS_CURRENT,
        "energy_since_car_connected": DEVICE_CLASS_ENERGY,
        "energy_total": DEVICE_CLASS_ENERGY,
        "charging_limit": DEVICE_CLASS_ENERGY,
        "charging_allowed": "go_echarger__allow_charging",
    },
}


def _setup_sensors(
    sensor_ids, sensors_config, coordinator_name, sensor_class, hass
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
                    f"sensor.go_echarger_{sensor_id}_{sensor}",
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
    hass,
    config_entry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    entry_id = config_entry.entry_id
    config = hass.data[DOMAIN][entry_id]
    _LOGGER.debug("Setting up the go-eCharger sensor for=%s", entry_id)

    if config_entry.options:
        config.update(config_entry.options)

    async_add_entities(
        _setup_sensors(
            [entry_id],
            CHARGER_SENSORS_CONFIG,
            f"{entry_id}_coordinator",
            ChargerSensor,
            hass,
        ),
        update_before_add=True,
    )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    """Set up go-eCharger Sensor platform."""
    _LOGGER.debug("Setting up the go-eCharger sensor platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    for charger_name in discovery_info[CONF_CHARGERS]:
        async_add_entities(
            _setup_sensors(
                [charger_name],
                CHARGER_SENSORS_CONFIG,
                f"{charger_name}_coordinator",
                ChargerSensor,
                hass,
            )
        )


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
    """Representation of a sensor for the go-eCharger."""

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_id,
            "manufacturer": "",
            "model": "",
        }

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        # if charging is not allowed, show current as 0
        if (
            self._attribute == "charger_max_current"
            and self.coordinator.data[self._device_id]["charging_allowed"] == "off"
        ):
            return 0

        # charging time is provided in the following format:
        # null=no charging in progress, type=0 counter going up, type=1 duration in ms
        # if the type is 1, we want to show the time
        if (
            self._attribute == "charging_duration"
            and "value" in self.coordinator.data[self._device_id][self._attribute]
            and self.coordinator.data[self._device_id][self._attribute]["type"] == 1
        ):
            return (
                self.coordinator.data[self._device_id][self._attribute]["value"]
                / MINUTE_IN_MS
            )

        if self.state_class == TIME_MINUTES:
            return (
                self.coordinator.data[self._device_id][self._attribute] / MINUTE_IN_MS
            )

        return self.coordinator.data[self._device_id][self._attribute]
