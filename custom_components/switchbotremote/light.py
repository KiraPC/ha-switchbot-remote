from typing import List
from homeassistant.components.light import LightEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from .client.remote import SupportedRemote

from .const import DOMAIN

IR_LIGHT_TYPES = [
    'DIY Light',
    'Light'
]

class SwitchBotRemoteLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, _id: str, name: str, options: dict = {}):
        super().__init__()
        self._hass = hass
        self.sb = sb
        self._unique_id = _id
        self._device_name = name
        self._power_sensor = options.get("power_sensor", None)
        self._state = STATE_OFF
        self._brightness = None

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model="Remote Light",
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._device_name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def state(self) -> str | None:
        return self._state

    @property
    def is_on(self):
        """Check if light is on."""
        return self._state

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._state = last_state.state

    async def async_turn_on(self, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOn")
        self._state = STATE_ON

    async def async_turn_off(self, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOff")
        self._state = STATE_OFF


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteLight(hass, remote, remote.id, remote.name)
        for remote in filter(lambda r: r.type in IR_LIGHT_TYPES, remotes)
    ]

    async_add_entities(entities, update_before_add=True)

    return True
