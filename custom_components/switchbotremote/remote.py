from homeassistant.components.remote import RemoteEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from switchbot import Remote

from .const import DOMAIN


class SwitchBotRemoteTV(RemoteEntity):
    _attr_has_entity_name = True

    def __init__(self, sb: Remote, _id: str, name: str) -> None:
        super().__init__()
        self.sb = sb
        self._attr_unique_id = _id
        self._is_on = False
        self._name = name

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="switchbot",
            name=self._name,
            model="TV Remote",
        )

    def turn_on(self, activity: str = None, **kwargs):
        """Send the power on command."""
        self.sb.turn("on")

    def turn_off(self, activity: str = None, **kwargs):
        """Send the power off command."""
        self.sb.turn("off")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    climates = [
        SwitchBotRemoteTV(remote, remote.id, remote.name)
        for remote in filter(lambda r: r.type == "TV", remotes)
    ]

    async_add_entities(climates)
