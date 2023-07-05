import base64
import hashlib
import hmac
import time
import logging
from typing import Any

import humps
from requests import request

_LOGGER = logging.getLogger(__name__)
switchbot_host = "https://api.switch-bot.com/v1.1"


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

    def request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{switchbot_host}/{path}"
        response = request(method, url, headers=self.headers, **kwargs)

        if response.status_code != 200:
            _LOGGER.debug("Received error", response.text)
            raise RuntimeError(f"SwitchBot API server returns status {response.status_code}")

        response_in_json = humps.decamelize(response.json())
        if response_in_json["status_code"] != 100:
            _LOGGER.debug("Received error", response_in_json)
            raise RuntimeError(f'An error occurred: {response_in_json["message"]}')

        return response_in_json

    def get(self, path: str, **kwargs) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> Any:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        return self.request("DELETE", path, **kwargs)