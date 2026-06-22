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
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from .client.remote import SupportedRemote

from .const import DOMAIN, MEDIA_CLASS, IR_MEDIA_TYPES, DIY_PROJECTOR_TYPE, PROJECTOR_TYPE, CONF_POWER_SENSOR, \
    MEDIA_PLAYER_COMMANDS, DIY_DVD_TYPE, DVD_TYPE, DIY_SPEAKER_TYPE, SPEAKER_TYPE, TV_TYPE, IPTV_TYPE, DIY_IPTV_TYPE, \
    DIY_TV_TYPE, SET_TOP_BOX_TYPE, DIY_SET_TOP_BOX_TYPE

_LOGGER = logging.getLogger(__name__)

IR_DVD_TYPES = [DVD_TYPE, DIY_DVD_TYPE]
IR_SPEAKER_TYPES = [SPEAKER_TYPE, DIY_SPEAKER_TYPE]

IR_TV_TYPES = [TV_TYPE, DIY_TV_TYPE]
IR_IPTV_TYPES = [DIY_IPTV_TYPE, IPTV_TYPE]
IR_PROJECTOR_TYPES = [DIY_PROJECTOR_TYPE, PROJECTOR_TYPE]
IR_SET_TOP_BOX_TYPES = [SET_TOP_BOX_TYPE, DIY_SET_TOP_BOX_TYPE]



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

        # Define supported features based on device type
        self._supported_features = MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF

        if not (sb.type in IR_DVD_TYPES):
            self._supported_features |= MediaPlayerEntityFeature.VOLUME_STEP

        if not (sb.type in IR_SET_TOP_BOX_TYPES):
            self._supported_features |= MediaPlayerEntityFeature.VOLUME_MUTE

        if sb.type in IR_IPTV_TYPES or sb.type in IR_TV_TYPES or sb.type in IR_SET_TOP_BOX_TYPES:
            self._supported_features |= MediaPlayerEntityFeature.VOLUME_STEP
            self._supported_features |= MediaPlayerEntityFeature.PLAY_MEDIA

        if sb.type in IR_IPTV_TYPES or sb.type in IR_DVD_TYPES or sb.type in IR_SPEAKER_TYPES or sb.type in IR_PROJECTOR_TYPES:
            self._supported_features |= MediaPlayerEntityFeature.PLAY
            if not (sb.type in IR_IPTV_TYPES):
                self._supported_features |= MediaPlayerEntityFeature.PAUSE

        if sb.type in IR_DVD_TYPES or sb.type in IR_SPEAKER_TYPES:
            self._supported_features |= MediaPlayerEntityFeature.PREVIOUS_TRACK
            self._supported_features |= MediaPlayerEntityFeature.NEXT_TRACK
            self._supported_features |= MediaPlayerEntityFeature.STOP

        # Load basic commands for this device type
        self._commands = MEDIA_PLAYER_COMMANDS.get(sb.type, {}).get("basic", {})

    async def send_command(self, *args):
        """Send a command using the SupportedRemote's command method."""
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


    async def async_turn_on(self):
        """Turn the media player on."""
        command_info = self._commands.get("turn_on")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self._state = STATE_IDLE if (self.sb.type in IR_SPEAKER_TYPES or self.sb.type in IR_DVD_TYPES) else STATE_ON
            self.async_write_ha_state()


    async def async_turn_off(self):
        """Turn the media player off."""
        command_info = self._commands.get("turn_off")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self._state = STATE_OFF
            self._source = None
            self.async_write_ha_state()


    async def async_volume_up(self):
        """Turn volume up for media player."""
        command_info = self._commands.get("volume_up")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_volume_down(self):
        """Turn volume down for media player."""
        command_info = self._commands.get("volume_down")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_mute_volume(self, mute):
        """Mute the volume."""
        command_info = self._commands.get("mute")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_media_play(self):
        """Play/Resume media."""
        command_info = self._commands.get("play")
        if command_info:
            self._state = STATE_PLAYING
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_media_pause(self):
        """Pause media."""
        command = "play" if self.sb.type in IR_IPTV_TYPES else "pause"
        command_info = self._commands.get(command)
        if command_info:
            self._state = STATE_PAUSED
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_media_play_pause(self):
        if self._state:
            await self.async_media_pause()
        else:
            await self.async_media_play()


    async def async_media_stop(self):
        """Stop media."""
        command_info = self._commands.get("stop")
        if command_info:
            self._state = STATE_IDLE
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_media_next_track(self):
        """Send next track command."""
        command_info = self._commands.get("next_track")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_media_previous_track(self):
        """Send previous track command."""
        command_info = self._commands.get("previous_track")
        if command_info:
            await self.send_command(command_info["action"], None, command_info["customize"])
            self.async_write_ha_state()


    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support channel change through play_media service."""
        if self._state == STATE_OFF:
            await self.async_turn_on()

        if media_type == "channel" and "set_channel" in self._commands:
            if not media_id.isdigit():
                _LOGGER.error("media_id must be a channel number")
                return
            command_info = self._commands["set_channel"]
            await self.send_command(command_info["action"], media_id, command_info["customize"])
            self._source = f"Channel {media_id}"
            self.async_write_ha_state()


    @callback
    def _async_update_power(self, state):
        """Update state based on power sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE:
                if state.state == STATE_OFF:
                    self._state = STATE_OFF
                    self._source = None
                elif state.state == STATE_ON:
                    self._state = STATE_IDLE if (self.sb.type in IR_DVD_TYPES or self.sb.type in IR_SPEAKER_TYPES) else STATE_ON
        except ValueError as ex:
            _LOGGER.error("Unable to update from power sensor: %s", ex)


    async def _async_power_sensor_changed(self, event: Event):
        """Handle power sensor changes."""
        new_state = event.data.get('new_state')
        if new_state is None:
            return
        self._async_update_power(new_state)
        self.async_write_ha_state()


    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if self._power_sensor:
            async_track_state_change_event(
                self.hass, [self._power_sensor], self._async_power_sensor_changed)
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
