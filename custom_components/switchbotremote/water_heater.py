from .const import DOMAIN, WATER_HEATER_CLASS, IR_WATER_HEATER_TYPES, CONF_POWER_SENSOR, CONF_TEMPERATURE_SENSOR, CONF_TEMP_MAX, CONF_TEMP_MIN
import logging
from typing import List
from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature, STATE_HEAT_PUMP
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF, STATE_ON
from homeassistant.const import UnitOfTemperature
from .client.remote import SupportedRemote

_LOGGER = logging.getLogger(__name__)


DEFAULT_MIN_TEMP = 40
DEFAULT_MAX_TEMP = 65


class SwitchBotRemoteWaterHeater(WaterHeaterEntity, RestoreEntity):
    _attr_has_entity_name = False
    _attr_operation_list = [STATE_OFF, STATE_HEAT_PUMP]

    def __init__(self, sb: SupportedRemote, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._device_name = sb.name
        self._attr_unique_id = sb.id
        self._is_on = False
        self._state = STATE_OFF
        self._temperature_unit = UnitOfTemperature.CELSIUS
        self._supported_features = WaterHeaterEntityFeature.OPERATION_MODE

        self._current_temperature = None
        self._power_sensor = options.get(CONF_POWER_SENSOR, None)
        self._temperature_sensor = options.get(CONF_TEMPERATURE_SENSOR, None)
        self._max_temp = options.get(CONF_TEMP_MAX, DEFAULT_MAX_TEMP)
        self._min_temp = options.get(CONF_TEMP_MIN, DEFAULT_MIN_TEMP)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=WATER_HEATER_CLASS + " Remote",
        )

    @property
    def name(self) -> str:
        """Return the display name of this water heater."""
        return self._device_name

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        """Return the list of supported features."""
        return self._supported_features

    @property
    def current_operation(self) -> str | None:
        """Return current operation."""
        return STATE_HEAT_PUMP if self._is_on else STATE_OFF

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._temperature_unit

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def max_temp(self):
        """Return the max temperature."""
        return self._max_temp

    @property
    def min_temp(self):
        """Return the min temperature."""
        return self._min_temp

    def turn_on(self, activity: str = None, **kwargs):
        """Send the power on command."""
        self.sb.command("turnOn")
        self._state = STATE_HEAT_PUMP
        self._is_on = True

    def turn_off(self, activity: str = None, **kwargs):
        """Send the power off command."""
        self.sb.command("turnOff")
        self._state = STATE_OFF
        self._is_on = False

    def set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode."""
        if operation_mode == STATE_HEAT_PUMP:
            self.turn_on()

        if operation_mode == STATE_OFF:
            self.turn_off()

    @callback
    def _async_update_temp(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE:
                self._current_temperature = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from temperature sensor: %s", ex)

    async def _async_temp_sensor_changed(self, entity_id, old_state, new_state):
        """Handle temperature sensor changes."""
        if new_state is None:
            return

        self._async_update_temp(new_state)
        await self.async_update_ha_state(force_refresh=True)

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE and state.state != self._state:
                if state.state == STATE_ON:
                    self._state = STATE_HEAT_PUMP
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

        if self._temperature_sensor:
            async_track_state_change(
                self.hass, self._temperature_sensor, self._async_temp_sensor_changed)

            temp_sensor_state = self.hass.states.get(self._temperature_sensor)
            if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                self._async_update_temp(temp_sensor_state)

        if self._power_sensor:
            async_track_state_change(
                self.hass, self._power_sensor, self._async_power_sensor_changed)

            power_sensor_state = self.hass.states.get(self._power_sensor)
            if power_sensor_state and power_sensor_state.state != STATE_UNKNOWN:
                self._async_update_power(power_sensor_state)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteWaterHeater(remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_WATER_HEATER_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
