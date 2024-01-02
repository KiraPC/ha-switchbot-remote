import logging
from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerEntityFeature
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from .client.remote import SupportedRemote

from .const import DOMAIN, MEDIA_CLASS, IR_MEDIA_TYPES, DIY_PROJECTOR_TYPE, PROJECTOR_TYPE, CONF_POWER_SENSOR

_LOGGER = logging.getLogger(__name__)

IR_TRACK_TYPES = [
    'DIY DVD',
    'DVD',
    'DIY Speaker',
    'Speaker',
]

IR_PROJECTOR_TYPES = [
    DIY_PROJECTOR_TYPE,
    PROJECTOR_TYPE,
]


class SwitchbotRemoteMediaPlayer(MediaPlayerEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._is_on = False
        self._state = STATE_OFF
        self._source = None

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)

        self._supported_features = MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        self._supported_features |= MediaPlayerEntityFeature.VOLUME_STEP
        self._supported_features |= MediaPlayerEntityFeature.VOLUME_MUTE
        self._supported_features |= MediaPlayerEntityFeature.PLAY_MEDIA

        if (sb.type in IR_TRACK_TYPES):
            self._supported_features |= MediaPlayerEntityFeature.PLAY
            self._supported_features |= MediaPlayerEntityFeature.PAUSE
            self._supported_features |= MediaPlayerEntityFeature.PREVIOUS_TRACK
            self._supported_features |= MediaPlayerEntityFeature.NEXT_TRACK
            self._supported_features |= MediaPlayerEntityFeature.STOP
        elif (sb.type in IR_PROJECTOR_TYPES):
            self._supported_features |= MediaPlayerEntityFeature.PLAY
            self._supported_features |= MediaPlayerEntityFeature.PAUSE
        else:
            self._supported_features |= MediaPlayerEntityFeature.PREVIOUS_TRACK
            self._supported_features |= MediaPlayerEntityFeature.NEXT_TRACK
            self._supported_features |= MediaPlayerEntityFeature.SELECT_SOURCE

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=MEDIA_CLASS + " Remote",
        )

    @property
    def should_poll(self):
        """Push an update after each command."""
        return True

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self._supported_features

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

    async def async_turn_off(self):
        """Turn the media player off."""
        await self.send_command("turnOff")

        self._state = STATE_OFF
        self._source = None

        self.async_write_ha_state()

    async def async_turn_on(self):
        """Turn the media player off."""
        await self.send_command("turnOn")

        self._state = STATE_IDLE if self.sb.type in IR_TRACK_TYPES else STATE_ON
        self.async_write_ha_state()

    async def async_media_previous_track(self):
        """Send previous track command."""
        if self.sb.type in IR_TRACK_TYPES:
            await self.send_command("Previous")
        else:
            await self.send_command("channelSub")
        self.async_write_ha_state()

    async def async_media_next_track(self):
        """Send next track command."""
        await self.send_command("Next")
        if self.sb.type in IR_TRACK_TYPES:
            await self.send_command("Next")
        else:
            await self.send_command("channelAdd")
        self.async_write_ha_state()

    async def async_volume_down(self):
        """Turn volume down for media player."""
        if self.sb.type in IR_PROJECTOR_TYPES:
            await self.send_command("VOL-", None, True)
        else:
            await self.send_command("volumeSub")

        self.async_write_ha_state()

    async def async_volume_up(self):
        """Turn volume up for media player."""
        if self.sb.type in IR_PROJECTOR_TYPES:
            await self.send_command("VOL+", None, True)
        else:
            await self.send_command("volumeAdd")

        self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        if self.sb.type in IR_PROJECTOR_TYPES:
            await self.send_command("MUTE", None, True)
        else:
            await self.send_command("setMute")

        self.async_write_ha_state()

    async def async_media_play(self):
        """Play/Resume media"""
        self._state = STATE_PLAYING

        if self.sb.type in IR_PROJECTOR_TYPES:
            await self.send_command("PLAY", None, True)
        else:
            await self.send_command("Play")

        self.async_write_ha_state()

    async def async_media_pause(self):
        """Pause media"""
        self._state = STATE_PAUSED

        if self.sb.type in IR_PROJECTOR_TYPES:
            await self.send_command("Paused", None, True)
        else:
            await self.send_command("Pause")

        self.async_write_ha_state()

    async def async_media_play_pause(self):
        """Play/Pause media"""
        self._state = STATE_PLAYING
        await self.send_command("Play")
        self.async_write_ha_state()

    async def async_media_stop(self):
        """Stop media"""
        self._state = STATE_IDLE
        await self.send_command("Stop")
        self.async_write_ha_state()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support channel change through play_media service."""
        if self._state == STATE_OFF:
            await self.async_turn_on()

        if not media_id.isdigit():
            _LOGGER.error("media_id must be a channel number")
            return

        self._source = "Channel {}".format(media_id)
        for digit in media_id:
            await self.send_command("SetChannel", digit, True)
        self.async_write_ha_state()

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE:
                if state.state == STATE_OFF:
                    self._state = STATE_OFF
                    self._source = None
                elif state.state == STATE_ON:
                    self._state = STATE_IDLE if self.sb.type in IR_TRACK_TYPES else STATE_ON

        except ValueError as ex:
            _LOGGER.error("Unable to update from power sensor: %s", ex)

    async def _async_power_sensor_changed(self, entity_id, old_state, new_state):
        """Handle power sensor changes."""
        if new_state is None:
            return

        self._async_update_power(new_state)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        if self._power_sensor:
            async_track_state_change(
                self.hass, self._power_sensor, self._async_power_sensor_changed)

            power_sensor_state = self.hass.states.get(self._power_sensor)
            if power_sensor_state and power_sensor_state.state != STATE_UNKNOWN:
                self._async_update_power(power_sensor_state)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchbotRemoteMediaPlayer(hass, remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_MEDIA_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
