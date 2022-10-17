"""Smart Energy state management"""

import logging
from .controller import fetch_status

from .const import (
    DOMAIN,
    CHARGERS_API,
)

_LOGGER = logging.getLogger(__name__)


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self):
        """Fetch go-eCharger car status via API."""

        _LOGGER.debug("Updating the go-eCharger coordinator data...")

        chargers_api = self._hass.data[DOMAIN][CHARGERS_API]
        data = self.coordinator.data if self.coordinator.data else {}
        _LOGGER.debug("Current go-eCharger coordinator data=%s", data)

        for charger_api_name in chargers_api.keys():
            data[charger_api_name] = await fetch_status(self._hass, charger_api_name)

        _LOGGER.debug("Updated go-eCharger coordinator data=%s", data)

        return data
