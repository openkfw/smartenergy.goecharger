"""Go-eCharger state (coordinator) management"""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME

from .const import CHARGERS_API, DOMAIN, INIT_STATE
from .controller import fetch_status

_LOGGER: logging.Logger = logging.getLogger(__name__)


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    async def fetch_states(self) -> dict:
        """Fetch go-eCharger car status via API."""

        _LOGGER.debug("Updating the go-eCharger coordinator data...")

        chargers_api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API]
        data = self.coordinator.data if self.coordinator.data else {}
        _LOGGER.debug("Current go-eCharger coordinator data=%s", data)

        for charger_name in chargers_api.keys():
            data[charger_name] = await fetch_status(self._hass, charger_name)
            data[charger_name][CONF_NAME] = chargers_api[charger_name][CONF_NAME]

        _LOGGER.debug("Updated go-eCharger coordinator data=%s", data)

        return data
