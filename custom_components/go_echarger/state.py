"""go-e Charger Cloud state (coordinator) management"""

import logging

from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType
from goechargerv2.goecharger import GoeChargerApi

from .const import (
    CHARGERS_API,
    API,
    DOMAIN,
    INIT_STATE,
)
from .controller import fetch_status

_LOGGER: logging.Logger = logging.getLogger(__name__)


def init_state(name: str, url: str, token: str) -> dict:
    """
    Initialize the state with go-e Charger Cloud API and static values.
    """

    return {
        CONF_NAME: name,
        API: GoeChargerApi(url, token),
    }


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass: HomeAssistantType) -> None:
        self._hass = hass

    async def fetch_states(self) -> dict:
        """
        Fetch go-e Charger Cloud car status via API.
        Fetched data will be enhanced with the:
        - friendly name of the charger
        """

        _LOGGER.debug("Updating the go-e Charger Cloud coordinator data...")

        chargers_api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API]
        current_data = self.coordinator.data if self.coordinator.data else {}
        _LOGGER.debug("Current go-e Charger Cloud coordinator data=%s", current_data)

        updated_data = {}

        for charger_name in chargers_api.keys():
            updated_data[charger_name] = await fetch_status(self._hass, charger_name)
            updated_data[charger_name][CONF_NAME] = chargers_api[charger_name][
                CONF_NAME
            ]

        _LOGGER.debug("Updated go-e Charger Cloud coordinator data=%s", updated_data)

        return updated_data
