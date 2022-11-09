"""Go-eCharger state (coordinator) management"""

import logging

from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from goechargerv2.goecharger import GoeChargerApi

from .const import (
    CHARGERS_API,
    API,
    DOMAIN,
    INIT_STATE,
    ENABLED,
    CHARGER_FORCE_CHARGING,
)
from .controller import fetch_status, start_charging, stop_charging

_LOGGER: logging.Logger = logging.getLogger(__name__)


def init_state(name: str, url: str, token: str) -> dict:
    """
    Initialize the state with Go-eCharger API and static values.
    """

    return {
        CONF_NAME: name,
        ENABLED: True,
        API: GoeChargerApi(url, token),
    }


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass: HomeAssistantType) -> None:
        self._hass = hass

    async def _handle_charging(
        self, is_enabled: bool, data: dict, charger_name: str
    ) -> None:
        """
        Handle automatic charging of a car. Charging is enabled/disabled based on the
        switch state and data received from the API, e.g. car status.
        """

        car_charging_status = data[CHARGER_FORCE_CHARGING]
        car_not_connected = data["car_status"] == "Charger ready, no car connected"

        if car_charging_status == "on":
            # turn charging off if:
            # - car is not connected
            # - or charging is disabled
            if car_not_connected or not is_enabled:
                _LOGGER.warning(
                    """Car %s is not connected or charging is manually disabled,
                    disabling charging""",
                    charger_name,
                )
                await stop_charging(self._hass, charger_name)
        else:
            # turn charging on if:
            # - charging is enabled
            # - and car is connected
            if is_enabled and not car_not_connected:
                _LOGGER.debug("Charging is enabled, starting to charge")
                await start_charging(self._hass, charger_name)

    async def fetch_states(self) -> dict:
        """
        Fetch go-eCharger car status via API.
        Fetched data will be enhanced with the:
        - friendly name of the charger
        - enabled/disabled status
        """

        _LOGGER.debug("Updating the go-eCharger coordinator data...")

        chargers_api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API]
        current_data = self.coordinator.data if self.coordinator.data else {}
        _LOGGER.debug("Current go-eCharger coordinator data=%s", current_data)

        updated_data = {}

        for charger_name in chargers_api.keys():
            # if enabled property is already present take it, otherwise set it to True
            is_enabled = (
                current_data[charger_name][ENABLED]
                if current_data
                and charger_name in current_data
                and ENABLED in current_data[charger_name]
                else True
            )

            # handle charging of a car
            if charger_name in current_data:
                await self._handle_charging(
                    is_enabled, current_data[charger_name], charger_name
                )

            updated_data[charger_name] = await fetch_status(self._hass, charger_name)
            updated_data[charger_name][CONF_NAME] = chargers_api[charger_name][
                CONF_NAME
            ]
            updated_data[charger_name][ENABLED] = is_enabled

        _LOGGER.debug("Updated go-eCharger coordinator data=%s", updated_data)

        return updated_data
