"""Go-eCharger state (coordinator) management"""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from goechargerv2.goecharger import GoeChargerApi

from .const import CHARGERS_API, API, DOMAIN, INIT_STATE, ENABLED
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

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

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
            is_enabled = (
                current_data[charger_name][ENABLED]
                if current_data and ENABLED in current_data[charger_name]
                else True
            )

            # if charging is enabled, start charging, otherwise stop charging
            if is_enabled:
                await start_charging(self._hass, charger_name)
            else:
                await stop_charging(self._hass, charger_name)

            updated_data[charger_name] = await fetch_status(self._hass, charger_name)
            updated_data[charger_name][CONF_NAME] = chargers_api[charger_name][
                CONF_NAME
            ]
            updated_data[charger_name][ENABLED] = is_enabled

        _LOGGER.debug("Updated go-eCharger coordinator data=%s", updated_data)

        return updated_data
