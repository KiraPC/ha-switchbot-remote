import logging
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .client.remote import SupportedRemote

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

SPEED_COMMANDS = [
    'lowSpeed',
    'middleSpeed',
    'highSpeed'
]

IR_FAN_TYPES = [
    'DIY Fan',
    'Fan'
]


class SwitchBotRemoteFan(FanEntity, RestoreEntity):
    _attr_has_entity_name = False
    _attr_speed_count = len(SPEED_COMMANDS)
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.OSCILLATE

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, _id: str, name: str, options: dict = {}) -> None:
        super().__init__()
        self._hass = hass
        self.sb = sb
        self._unique_id = _id
        self._device_name = name
        self._is_on = False
        self._is_oscillating = False
        self._power_sensor = options.get("power_sensor", None)
        self._state = STATE_OFF
        self._speed = SPEED_COMMANDS[0]

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            model="Fan Remote",
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
    def state(self) -> str | None:
        return self._state

    @property
    def is_on(self):
        """Check if fan is on."""
        return self._state

    @property
    def percentage(self):
        """Return the current speed percentage."""
        return ordered_list_item_to_percentage(SPEED_COMMANDS, self._speed)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._state = last_state.state

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        speed = percentage_to_ordered_list_item(SPEED_COMMANDS, percentage)
        await self.send_command(speed)
        self._speed = speed

    async def async_oscillate(self, oscillating: bool) -> None:
        """Oscillate the fan."""
        await self.send_command("swing")
        self._is_oscillating = oscillating

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
) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteFan(remote, hass, remote.id,
                           remote.name, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_FAN_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
