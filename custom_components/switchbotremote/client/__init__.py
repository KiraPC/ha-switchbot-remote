import uuid
from typing import List

from .client import SwitchBotClient
from .remote import Remote

from homeassistant.exceptions import ServiceValidationError

__version__ = "2.3.1"


class SwitchBot:
    def __init__(self, token: str, secret: str):
        self.client = SwitchBotClient(token, secret, nonce=str(uuid.uuid4()))

    def remotes(self) -> List[Remote]:
        response = self.client.get("devices")
        return [
            Remote.create(client=self.client, id=remote["device_id"], **remote)
            for remote in response["body"]["infrared_remote_list"]
        ]

    def remote(self, id: str) -> Remote:
        for remote in self.remotes():
            if remote.id == id:
                return remote
        raise ServiceValidationError(f"Unknown remote {id}")
