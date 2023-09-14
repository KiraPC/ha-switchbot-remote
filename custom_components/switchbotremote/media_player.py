import logging
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.media_player.const import (
    SUPPORT_TURN_OFF, SUPPORT_TURN_ON, SUPPORT_PREVIOUS_TRACK,
    SUPPORT_NEXT_TRACK, SUPPORT_VOLUME_STEP, SUPPORT_VOLUME_MUTE,
    SUPPORT_PLAY_MEDIA, SUPPORT_SELECT_SOURCE, MEDIA_TYPE_CHANNEL)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .client.remote import SupportedRemote

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

IR_MEDIA_TYPES = [
    'DIY TV',
    'TV',
    'DIY IPTV',
    'IPTV',
    'DIY DVD',
    'DVD',
    'DIY Speaker',
    'Speaker',
    'DIY Set Top Box',
    'Set Top Box',
]

IR_TRACK_TYPES = [
    'DIY DVD',
    'DVD',
    'DIY Speaker',
    'Speaker',
    'DIY Projector',
    'Projector'
]


class SwitchbotRemoteMediaPlayer(MediaPlayerEntity, RestoreEntity):
    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, _id: str, name: str, options: dict = {}) -> None:
        super().__init__()
        self._hass = hass
        self.sb = sb
        self._unique_id = _id
        self._is_on = False
        self._device_name = name
        self._power_sensor = options.get("power_sensor", None)
        self._state = STATE_OFF
        self._source = None

        self._support_flags = SUPPORT_TURN_OFF | SUPPORT_TURN_ON | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_PLAY_MEDIA | SUPPORT_SELECT_SOURCE

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model="Media Remote",
        )

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._state = last_state.state

    @property
    def should_poll(self):
        """Push an update after each command."""
        return True

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the media player."""
        return self._device_name

    @property
    def state(self):
        """Return the state of the player."""
        return self._state

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self._support_flags

    async def async_turn_off(self):
        """Turn the media player off."""
        await self.send_command("turnOff")

        if self._power_sensor is None:
            self._state = STATE_OFF
            self._source = None
            await self.async_update_ha_state()

    async def async_turn_on(self):
        """Turn the media player off."""
        await self.send_command("turnOn")

        if self._power_sensor is None:
            self._state = STATE_ON
            await self.async_update_ha_state()

    async def async_media_previous_track(self):
        """Send previous track command."""
        if self.sb.type in IR_TRACK_TYPES:
            await self.send_command("Previous")
        else:
            await self.send_command("channelSub")
        await self.async_update_ha_state()

    async def async_media_next_track(self):
        """Send next track command."""
        if self.sb.type in IR_TRACK_TYPES:
            await self.send_command("Next")
        else:
            await self.send_command("channelAdd")
        await self.async_update_ha_state()

    async def async_volume_down(self):
        """Turn volume down for media player."""
        await self.send_command("volumeSub")
        await self.async_update_ha_state()

    async def async_volume_up(self):
        """Turn volume up for media player."""
        await self.send_command("volumeAdd")
        await self.async_update_ha_state()

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        await self.send_command("setMute")
        await self.async_update_ha_state()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support channel change through play_media service."""
        if self._state == STATE_OFF:
            await self.async_turn_on()

        if self.sb.type in IR_TRACK_TYPES:
            await self.send_command("Play")
            await self.async_update_ha_state()
            return

        if media_type != MEDIA_TYPE_CHANNEL:
            LOGGER.error("invalid media type")
            return
        if not media_id.isdigit():
            LOGGER.error("media_id must be a channel number")
            return

        self._source = "Channel {}".format(media_id)
        for digit in media_id:
            await self.send_command("SetChannel", digit, True)
        await self.async_update_ha_state()

    async def async_update(self):
        if self._power_sensor is None:
            return

        power_state = self.hass.states.get(self._power_sensor)

        if power_state:
            if power_state.state == STATE_OFF:
                self._state = STATE_OFF
                self._source = None
            elif power_state.state == STATE_ON:
                self._state = STATE_ON


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchbotRemoteMediaPlayer(
            hass, remote, remote.id, remote.name, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_MEDIA_TYPES, remotes)
    ]

    async_add_entities(entities)
