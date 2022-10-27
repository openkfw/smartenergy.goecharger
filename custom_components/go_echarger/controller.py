"""API controller configuration for Go-eCharger integration"""

import logging

from homeassistant.core import HomeAssistant
from .const import API, CHARGERS_API, DOMAIN, INIT_STATE

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def fetch_status(hass: HomeAssistant, charger_name: str) -> dict:
    """Fetch go-eCharger car status via API."""

    api = hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]
    fetched_status = await hass.async_add_executor_job(api.request_status)

    return fetched_status


class ChargerController:
    """Represents go-eCharger controller, abstracting API calls into methods."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def _is_charging_allowed(self, charger_name: str) -> bool:
        """Check if charging is allowed. If not, log an error and return False, other return True"""

        if (
            self._hass.data[DOMAIN][f"{charger_name}_coordinator"].data[charger_name][
                "charging_allowed"
            ]
            == "off"
        ):
            _LOGGER.error(
                """Charging for the %s is not allowed, please authenticate the car
                 to allow automated charging""",
                charger_name,
            )
            return False

        return True

    async def start_charging(self, call: dict) -> None:
        """Get name and assigned power from the service call and call the API accordingly.
        In case charging is not allowed, log a warning and early escape."""

        charger_name = call.data.get("device_name", None)
        charging_power = call.data.get("charging_power", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not self._is_charging_allowed:
            _LOGGER.warning("Charging is currently not allowed")
            return

        _LOGGER.debug(
            "Starting charging for the device=%s with power=%s",
            charger_name,
            charging_power,
        )

        if charging_power is not None:
            await self._hass.async_add_executor_job(api.set_max_current, charging_power)

        await self._hass.async_add_executor_job(api.set_force_charging, True)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def stop_charging(self, call: dict) -> None:
        """Get name and assigned power from the service call and call the API accordingly.
        In case charging is not allowed, log a warning and early escape."""

        charger_name = call.data.get("device_name", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not self._is_charging_allowed:
            _LOGGER.warning("Charging is currently not allowed")
            return

        _LOGGER.debug("Stopping charging for the device=%s", charger_name)

        await self._hass.async_add_executor_job(api.set_max_current, 0)
        await self._hass.async_add_executor_job(api.set_force_charging, False)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def change_charging_power(self, call: dict) -> None:
        """Get name and power from the service call and call the API accordingly.
        In case charging is not allowed, log an error and early escape."""

        charger_name = call.data.get("device_name", None)
        charging_power = call.data.get("charging_power", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not self._is_charging_allowed:
            return

        _LOGGER.debug(
            "Changing charging power for the device=%s to power=%s",
            charger_name,
            charging_power,
        )

        await self._hass.async_add_executor_job(api.set_max_current, charging_power)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def set_phase(self, call: dict) -> None:
        """Get name and phase from the service call and call the API accordingly.
        In case the phase value is not set correctly, log an error and early escape.
        Possible phase values: 0 (Auto), 1 (1-phased), 2 (3-phased)
        """

        charger_name = call.data.get("device_name", None)
        phase = call.data.get("phase", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not phase in [0, 1, 2]:
            return

        _LOGGER.debug(
            "Setting phase for device=%s to %s",
            charger_name,
            phase,
        )

        await self._hass.async_add_executor_job(api.set_phase, phase)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def set_authentication(self, call: dict) -> None:
        """Get name and status from the service call and call the API accordingly.
        In case the status value is not set correctly, log an error and early escape.
        Possible values: 0 (open), 1 (wait)
        """

        charger_name = call.data.get("device_name", None)
        status = call.data.get("status", None)
        api = self._hass.data[DOMAIN][INIT_STATE]["apis"][charger_name][API]

        if not status in [0, 1]:
            return

        _LOGGER.debug(
            "Setting authentication status for device=%s to %s",
            charger_name,
            status,
        )

        await self._hass.async_add_executor_job(api.set_access_control, status)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()
