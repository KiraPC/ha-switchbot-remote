import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF, STATE_ON
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from .client.remote import SupportedRemote

from .const import (
    DOMAIN,
    IR_CLIMATE_TYPES,
    AIR_CONDITIONER_CLASS,
    CONF_POWER_SENSOR,
    CONF_TEMPERATURE_SENSOR,
    CONF_HUMIDITY_SENSOR,
    CONF_TEMP_MIN,
    CONF_TEMP_MAX,
    CONF_TEMP_STEP,
    CONF_HVAC_MODES,
    CONF_OVERRIDE_OFF_COMMAND,
)
from .config_flow import DEFAULT_HVAC_MODES

_LOGGER = logging.getLogger(__name__)

HVAC_REMOTE_MODES = {
    HVACMode.OFF: 1,
    HVACMode.COOL: 2,
    HVACMode.DRY: 3,
    HVACMode.AUTO: 1,
    HVACMode.FAN_ONLY: 4,
    HVACMode.HEAT: 5,
}

FAN_REMOTE_MODES = {
    FAN_AUTO: 1,
    FAN_LOW: 2,
    FAN_MEDIUM: 3,
    FAN_HIGH: 4,
}

DEFAULT_MIN_TEMP = 16
DEFAULT_MAX_TEMP = 30


class SwitchBotRemoteClimate(ClimateEntity, RestoreEntity):
    _attr_has_entity_name = False
    _attr_force_update = True

    def __init__(self, sb: SupportedRemote, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._unique_id = sb.id
        self._device_name = sb.name
        self._is_on = False
        self.options = options

        self._last_on_operation = None
        self._operation_modes = options.get(
            CONF_HVAC_MODES, DEFAULT_HVAC_MODES)

        if HVACMode.OFF not in self._operation_modes:
            self._operation_modes.append(HVACMode.OFF)

        self._hvac_mode = HVACMode.OFF

        self._temperature_unit = UnitOfTemperature.CELSIUS
        self._target_temperature = 28
        self._target_temperature_step = options.get(CONF_TEMP_STEP, 1)
        self._max_temp = options.get(CONF_TEMP_MAX, DEFAULT_MAX_TEMP)
        self._min_temp = options.get(CONF_TEMP_MIN, DEFAULT_MIN_TEMP)
        self._power_sensor = options.get(CONF_POWER_SENSOR, None)
        self._override_off_command = options.get(CONF_OVERRIDE_OFF_COMMAND, True)

        self._fan_mode = FAN_AUTO
        self._fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
        ]

        self._supported_features = ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE

        self._temperature_sensor = options.get(CONF_TEMPERATURE_SENSOR, None)
        self._humidity_sensor = options.get(CONF_HUMIDITY_SENSOR, None)
        self._current_temperature = None
        self._current_humidity = None

        # ClimateEntityFeature migration done
        # This line will be removed after deprecation period (until 2025.1)
        # https://developers.home-assistant.io/blog/2024/01/24/climate-climateentityfeatures-expanded/
        self._enable_turn_on_off_backwards_compatibility = False

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=AIR_CONDITIONER_CLASS + " Remote",
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the display name of this A/C."""
        return self._device_name

    @property
    def state(self):
        """Return the current state."""
        if self.hvac_mode != HVACMode.OFF:
            return self.hvac_mode
        return HVACMode.OFF

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._operation_modes

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._fan_modes

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self._fan_mode

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac mode ie. heat, cool."""
        return self._hvac_mode  # type: ignore

    @property
    def power_state(self):
        return "on" if self._is_on else "off"

    @property
    def last_on_operation(self):
        """Return the last non-idle operation ie. heat, cool."""
        return self._last_on_operation

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._temperature_unit

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self._target_temperature_step

    @property
    def max_temp(self):
        """Return the max temperature."""
        return self._max_temp

    @property
    def min_temp(self):
        """Return the min temperature."""
        return self._min_temp

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._supported_features

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._current_humidity

    @property
    def extra_state_attributes(self):
        """Platform specific attributes."""
        return {
            'last_on_operation': self._last_on_operation
        }

    def turn_off(self):
        """Turn off."""
        self.set_hvac_mode(HVACMode.OFF)

    def turn_on(self):
        """Turn on."""
        self.set_hvac_mode(self._last_on_operation or HVACMode.COOL)

    def set_temperature(self, **kwargs):
        self._target_temperature = kwargs.get("temperature")

        self._update_remote()

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF and self._override_off_command:
            self.sb.turn("off")
            self._is_on = False
        else:
            self._last_on_operation = hvac_mode

        self._is_on = True
        self._hvac_mode = hvac_mode
        self._update_remote()

    def set_fan_mode(self, fan_mode):
        self._fan_mode = fan_mode
        self._update_remote()

    def _update_remote(self):
        if (self._hvac_mode != HVACMode.OFF and self._override_off_command):
            self.sb.command(
                "setAll",
                f"{self.target_temperature},{HVAC_REMOTE_MODES[self.hvac_mode]},{FAN_REMOTE_MODES[self.fan_mode]},{self.power_state}",
            )

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
    def _async_update_humidity(self, state):
        """Update thermostat with latest state from humidity sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE:
                self._current_humidity = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from humidity sensor: %s", ex)

    async def _async_humidity_sensor_changed(self, entity_id, old_state, new_state):
        """Handle humidity sensor changes."""
        if new_state is None:
            return

        self._async_update_humidity(new_state)
        await self.async_update_ha_state(force_refresh=True)

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE:
                if state.state == STATE_OFF:
                    self._is_on = False
                    self._hvac_mode = HVACMode.OFF
                elif state.state == STATE_ON:
                    self._is_on = True
                    self._hvac_mode = self._last_on_operation
        except ValueError as ex:
            _LOGGER.error("Unable to update from power sensor: %s", ex)

    async def _async_power_sensor_changed(self, entity_id, old_state, new_state):
        """Handle power sensor changes."""
        if new_state is None:
            return

        self._async_update_power(new_state)
        await self.async_update_ha_state(force_refresh=True)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._hvac_mode = last_state.state
            self._fan_mode = last_state.attributes.get('fan_mode') or FAN_AUTO
            self._target_temperature = last_state.attributes.get(
                'temperature') or 28
            self._last_on_operation = last_state.attributes.get(
                'last_on_operation')

        if self._temperature_sensor:
            async_track_state_change(
                self.hass, self._temperature_sensor, self._async_temp_sensor_changed)

            temp_sensor_state = self.hass.states.get(self._temperature_sensor)
            if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                self._async_update_temp(temp_sensor_state)

        if self._humidity_sensor:
            async_track_state_change(
                self.hass, self._humidity_sensor, self._async_humidity_sensor_changed)

            humidity_sensor_state = self.hass.states.get(self._humidity_sensor)
            if humidity_sensor_state and humidity_sensor_state.state != STATE_UNKNOWN:
                self._async_update_humidity(humidity_sensor_state)

        if self._power_sensor:
            async_track_state_change(
                self.hass, self._power_sensor, self._async_power_sensor_changed)

            power_sensor_state = self.hass.states.get(self._power_sensor)
            if power_sensor_state and power_sensor_state.state != STATE_UNKNOWN:
                self._async_update_power(power_sensor_state)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteClimate(remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_CLIMATE_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
