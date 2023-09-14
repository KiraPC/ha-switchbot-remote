import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from .client.remote import SupportedRemote

from .const import DOMAIN

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

IR_CLIMATE_TYPES = [
    'DIY Air Conditioner',
    'Air Conditioner'
]


class SwitchBotRemoteClimate(ClimateEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, sb: SupportedRemote, _id: str, name: str, options: dict = {}) -> None:
        super().__init__()
        self.sb = sb
        self._unique_id = _id
        self._is_on = False
        self._name = name
        self.options = options

        self._last_on_operation = None
        self._operation_modes = [
            HVACMode.OFF,
            HVACMode.COOL,
            HVACMode.DRY,
            HVACMode.FAN_ONLY,
            HVACMode.HEAT,
        ]

        self._hvac_mode = HVACMode.OFF

        self._temperature_unit = TEMP_CELSIUS
        self._target_temperature = 28
        self._target_temperature_step = 1

        self._fan_mode = FAN_AUTO
        self._fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
        ]

        self._supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
        )

        self._temperature_sensor = options.get("temperature_sensor", None)
        self._humidity_sensor = options.get("umidity_sensor", None)
        self._current_temperature = None
        self._current_humidity = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._name,
            model="Air Conditioner",
        )

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

    def turn_on(self):
        """Turn on."""
        self.set_hvac_mode(self._last_on_operation or HVACMode.COOL)

    def set_temperature(self, **kwargs):
        self._target_temperature = kwargs.get("temperature")

        self._update_remote()

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == "off":
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
        await self.async_update_ha_state()

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
        await self.async_update_ha_state()

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
            async_track_state_change(self.hass, self._temperature_sensor,
                                     self._async_temp_sensor_changed)

            temp_sensor_state = self.hass.states.get(self._temperature_sensor)
            if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                self._async_update_temp(temp_sensor_state)

        if self._humidity_sensor:
            async_track_state_change(self.hass, self._humidity_sensor,
                                     self._async_humidity_sensor_changed)

            humidity_sensor_state = self.hass.states.get(self._humidity_sensor)
            if humidity_sensor_state and humidity_sensor_state.state != STATE_UNKNOWN:
                self._async_update_humidity(humidity_sensor_state)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteClimate(
            remote, remote.id, remote.name, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_CLIMATE_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
