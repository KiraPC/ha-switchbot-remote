import logging
from typing import List
from homeassistant.components.remote import RemoteEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF, STATE_ON
from .client.remote import SupportedRemote

from .const import DOMAIN, OTHERS_TYPE, CLASS_BY_TYPE, CONF_POWER_SENSOR, CONF_ON_COMMAND, CONF_OFF_COMMAND

_LOGGER = logging.getLogger(__name__)


class SwitchBotRemoteOther(RemoteEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, sb: SupportedRemote, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._device_name = sb.name
        self._attr_unique_id = sb.id
        self._is_on = False

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)
        self._on_command = options.get(CONF_ON_COMMAND, None)
        self._off_command = options.get(CONF_OFF_COMMAND, None)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=CLASS_BY_TYPE[self.sb.type] + " Remote",
        )

    @property
    def name(self) -> str:
        """Return the display name of this remote."""
        return self._device_name

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, activity: str = None, **kwargs):
        """Send the power on command."""
        if self._on_command:
            self.sb.command(self._on_command)

    def turn_off(self, activity: str = None, **kwargs):
        """Send the power off command."""
        if self._off_command:
            self.sb.command(self._off_command)
        elif self._on_command:
            self.sb.command(self._on_command)

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE and state.state != self._is_on:
                self._is_on = state.state == STATE_ON
        except ValueError as ex:
            _LOGGER.error("Unable to update from power sensor: %s", ex)

    async def _async_power_sensor_changed(self, entity_id, old_state, new_state):
        """Handle power sensor changes."""
        if new_state is None:
            return

        self._async_update_power(new_state)

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
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for remote in remotes:
        options = entry.data.get(remote.id, {})

        if (remote.type == OTHERS_TYPE and options.get("on_command", None)):
            entities.append(SwitchBotRemoteOther(remote, options))

    _LOGGER.debug(f'Adding remotes {entities}')
    async_add_entities(entities)

    return True
