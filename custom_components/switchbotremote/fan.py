import logging
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF, STATE_ON
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from .client.remote import SupportedRemote

from .const import (
    DOMAIN,
    IR_FAN_TYPES,
    FAN_CLASS,
    AIR_PURIFIER_TYPE,
    DIY_AIR_PURIFIER_TYPE,
    CONF_WITH_SPEED,
    CONF_POWER_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

SPEED_COMMANDS = [
    "lowSpeed",
    "middleSpeed",
    "highSpeed",
]

AIR_PURIFIER_SPEED_COMMANDS = [
    "FAN SPEED 1",
    "FAN SPEED 2",
    "FAN SPEED 3",
]

IR_AIR_PURIFIER_TYPES = [
    DIY_AIR_PURIFIER_TYPE,
    AIR_PURIFIER_TYPE,
]


class SwitchBotRemoteFan(FanEntity, RestoreEntity):
    _attr_has_entity_name = False
    _attr_speed_count = len(SPEED_COMMANDS)

    def __init__(
        self, hass: HomeAssistant, sb: SupportedRemote, options: dict = {}
    ) -> None:
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._is_on = False
        self._is_oscillating = False
        self._state = STATE_OFF
        self._speed = (
            AIR_PURIFIER_SPEED_COMMANDS[0]
            if sb.type in IR_AIR_PURIFIER_TYPES
            else SPEED_COMMANDS[0]
        )
        self._supported_features = 0

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)

        if options.get(CONF_WITH_SPEED, None):
            self._supported_features = FanEntityFeature.SET_SPEED

        if sb.type not in IR_AIR_PURIFIER_TYPES:
            self._supported_features |= FanEntityFeature.OSCILLATE

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=FAN_CLASS + " Remote",
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the display name of this fan."""
        return self._device_name

    @property
    def state(self) -> str | None:
        return self._state

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._supported_features

    @property
    def is_on(self):
        """Check if fan is on."""
        return self._state

    @property
    def percentage(self):
        """Return the current speed percentage."""
        return ordered_list_item_to_percentage(
            AIR_PURIFIER_SPEED_COMMANDS
            if self.sb.type in IR_AIR_PURIFIER_TYPES
            else SPEED_COMMANDS,
            self._speed,
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        speed = percentage_to_ordered_list_item(
            AIR_PURIFIER_SPEED_COMMANDS
            if self.sb.type in IR_AIR_PURIFIER_TYPES
            else SPEED_COMMANDS,
            percentage,
        )
        await self.send_command(speed)
        self._speed = speed

    async def async_oscillate(self, oscillating: bool) -> None:
        """Oscillate the fan."""
        await self.send_command("swing")
        self._is_oscillating = oscillating

    async def async_turn_on(self, percentage: int = None, preset_mode: str = None, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOn")

        self._state = STATE_ON
        self._is_on = True

        if percentage is None:
            percentage = self.percentage

        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOff")
        self._state = STATE_OFF
        self._is_on = False

    @callback
    def _async_update_power(self, state):
        """Update thermostat with latest state from temperature sensor."""
        try:
            if (
                state.state != STATE_UNKNOWN
                and state.state != STATE_UNAVAILABLE
                and state.state != self._state
            ):
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
                self.hass, self._power_sensor, self._async_power_sensor_changed
            )

            power_sensor_state = self.hass.states.get(self._power_sensor)
            if power_sensor_state and power_sensor_state.state != STATE_UNKNOWN:
                self._async_update_power(power_sensor_state)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteFan(hass, remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_FAN_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
