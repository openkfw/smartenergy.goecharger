"""Mock API module."""

from http.client import BAD_REQUEST, OK

from custom_components.go_echarger.const import CHARGER_ACCESS, CHARGER_MAX_CURRENT

# pylint: disable=unused-argument
def mocked_api_requests(*args, **kwargs) -> dict | int:
    """Module handling mocked API requests."""

    class MockResponse:
        """Class handling mocked API responses"""

        def __init__(self, json_data: dict, status_code: int) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def request_status(self) -> dict:
            """Return data as a JSON"""
            return self.json_data

        def set_force_charging(self, val: bool) -> bool:
            """Return provided value and update data"""
            self.json_data["charger_force_charging"] = "on" if val else "off"
            return val

        def set_access_control(self, val: int) -> int:
            """Return provided value and update data"""
            self.json_data[CHARGER_ACCESS] = bool(not val)
            return val

        def set_max_current(self, val: int) -> int:
            """Return provided value and update data"""
            self.json_data[CHARGER_MAX_CURRENT] = val
            return val

    if args[0] in ["http://1.1.1.1", "http://1.1.1.2"]:
        # use .copy() to not mutate the original data
        return MockResponse(kwargs["data"].copy(), OK)

    return BAD_REQUEST
