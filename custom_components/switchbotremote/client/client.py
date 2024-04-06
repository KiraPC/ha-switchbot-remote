import base64
import hashlib
import hmac
import time
import logging
from typing import Any

import humps
import time
from requests import request

from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)
switchbot_host = "https://api.switch-bot.com/v1.1"

MAX_TRIES = 5
DELAY_BETWEEN_TRIES_MS = 500

class SwitchBotClient:
    def __init__(self, token: str, secret: str, nonce: str):
        self._token = token
        self._secret = secret
        self._nonce = nonce

    @property
    def headers(self):
        headers = dict()

        timestamp = int(round(time.time() * 1000))
        signature = f"{self._token}{timestamp}{self._nonce}"
        signature = base64.b64encode(
            hmac.new(
                self._secret.encode(),
                msg=signature.encode(),
                digestmod=hashlib.sha256,
            ).digest()
        )

        headers["Authorization"] = self._token
        headers["t"] = str(timestamp)
        headers["sign"] = signature
        headers["nonce"] = self._nonce

        return headers

    def __request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{switchbot_host}/{path}"
        _LOGGER.debug(f"Calling service {url}")
        response = request(method, url, headers=self.headers, **kwargs)

        if response.status_code != 200:
            _LOGGER.debug(f"Received http error {response.status_code} {response.text}")
            if response.status_code != 500:
                raise HomeAssistantError(f"SwitchBot API server returns status {response.status_code}")
            else:
                raise SwitchbotInternal500Error

        response_in_json = humps.decamelize(response.json())
        if response_in_json["status_code"] != 100:
            _LOGGER.debug(f"Received error in response {response_in_json}")
            raise HomeAssistantError(f'An error occurred: {response_in_json["message"]}')

        _LOGGER.debug(f"Call service {url} OK")
        return response_in_json
    
    def request(self, method: str, path: str, maxNumberOfTrials: int = MAX_TRIES, delayMSBetweenTrials: int = DELAY_BETWEEN_TRIES_MS, **kwargs) -> Any:
        """Try to send the request.
        If the server returns a 500 Internal error status, will retry until it succeeds or it passes a threshold of max number of tries.
        Any other error will be thrown."""
        for tryNumber in range(maxNumberOfTrials):
            try:
                result = self.__request(method, path, **kwargs)
                return result
            except SwitchbotInternal500Error:
                _LOGGER.warning("Caught returned status 500 from SwitchBot API server")
                _LOGGER.debug(f"tryNumber = {tryNumber}, waiting {delayMSBetweenTrials} ms")
                time.sleep(delayMSBetweenTrials / 1000)
        else:
            # The following exception is only raised if all the request attempts have thrown a 500 error code
            raise SwitchbotInternal500Error(f"Received multiple ({maxNumberOfTrials}) consecutive 500 errors from SwitchBot API server")

    def get(self, path: str, **kwargs) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> Any:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        return self.request("DELETE", path, **kwargs)

class SwitchbotInternal500Error(HomeAssistantError):
    """Exception raised if the 500 status error has been received from Switchbot cloud API"""
