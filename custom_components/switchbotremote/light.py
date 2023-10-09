import logging
from typing import List
from homeassistant.components.light import LightEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF, STATE_ON
from .client.remote import SupportedRemote

from .const import DOMAIN, IR_LIGHT_TYPES, LIGHT_CLASS, CONF_POWER_SENSOR

_LOGGER = logging.getLogger(__name__)


class SwitchBotRemoteLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._state = STATE_OFF
        self._brightness = None

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=LIGHT_CLASS + " Remote",
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
        """Send the power off command."""
        await self.send_command("turnOff")
        self._state = STATE_OFF

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE and state.state != self._state:
                if state.state == STATE_ON:
                    self._state = STATE_ON
                    self._is_on = True
                else:
                    self._state = STATE_OFF
                    self._is_on = False
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

    entities = [
        SwitchBotRemoteLight(hass, remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_LIGHT_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
