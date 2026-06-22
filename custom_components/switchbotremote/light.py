import logging
from typing import List, Any
from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntityFeature,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    STATE_OFF,
    STATE_ON
)
from .client.remote import SupportedRemote

from .const import DOMAIN, IR_LIGHT_TYPES, LIGHT_CLASS, CONF_POWER_SENSOR

_LOGGER = logging.getLogger(__name__)


class SwitchBotRemoteLight(LightEntity, RestoreEntity):
    """
    Representation of a SwitchBot Remote Light for Home Assistant.
    """

    _attr_has_entity_name = False  # Keep if you really don't want HA to manage the name
    # Define the brightness step for each brightness up/down command
    BRIGHTNESS_STEP = 25  # This will give approximately 10 steps (255/25)

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, options: dict = {}) -> None:
        """
        Initialize the SwitchBotRemoteLight entity.

        Args:
            hass (HomeAssistant): The Home Assistant instance.
            sb (SupportedRemote): A SwitchBot remote object with ID and name.
            options (dict): Additional configuration options.
        """
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._state = STATE_OFF  # Keep _state for backwards compatibility

        # Color mode configuration
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_brightness = 255  # Default to full brightness when turned on

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return device info so this entity is grouped correctly in Home Assistant.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=f"{LIGHT_CLASS} Remote",
        )

    @property
    def unique_id(self) -> str:
        """
        Return a unique ID for this entity.
        """
        return self._unique_id

    @property
    def name(self) -> str:
        """
        Return the friendly name of this light entity.
        """
        return self._device_name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._attr_brightness

    @property
    def state(self) -> str | None:
        """Return the state of the entity."""
        return self._state

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state == STATE_ON

    async def async_added_to_hass(self) -> None:
        """
        Called when this entity is added to Home Assistant.

        - Restores the previous on/off state.
        - Sets up the power sensor listener if provided.
        """
        await super().async_added_to_hass()

        # Restore previous state (if available) from the recorder
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._state = last_state.state
            # Restore brightness if it was saved
            if last_state.attributes.get(ATTR_BRIGHTNESS) is not None:
                self._attr_brightness = last_state.attributes.get(ATTR_BRIGHTNESS)

        # If a power sensor is defined, track changes to keep the light's state in sync
        if self._power_sensor:
            async_track_state_change_event(
                self.hass,
                [self._power_sensor],
                self._async_power_sensor_changed
            )
            power_sensor_state = self.hass.states.get(self._power_sensor)
            if power_sensor_state and power_sensor_state.state != STATE_UNKNOWN:
                self._async_update_power(power_sensor_state)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        # Process brightness if provided
        if ATTR_BRIGHTNESS in kwargs:
            target_brightness = kwargs[ATTR_BRIGHTNESS]
            # If light is already on, adjust brightness
            if self.is_on and self._attr_brightness != target_brightness:
                await self._async_set_brightness(target_brightness)
            else:
                # Store the brightness to be applied when turning on
                self._attr_brightness = target_brightness

        # Turn on the light
        await self.send_command("turnOn")
        self._state = STATE_ON
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.send_command("turnOff")
        self._state = STATE_OFF
        self.async_write_ha_state()

    async def _async_set_brightness(self, brightness):
        """Set the brightness by sending multiple brightnessUp/Down commands."""
        if not self.is_on:
            # If light is off, we should turn it on first
            await self.send_command("turnOn")
            self._state = STATE_ON

        # Calculate how many steps to take
        if brightness > self._attr_brightness:
            # Need to increase brightness
            while self._attr_brightness < brightness:
                await self._async_brightness_up()
                # Break if we've reached or exceeded the target
                if self._attr_brightness >= brightness:
                    break
        elif brightness < self._attr_brightness:
            # Need to decrease brightness
            while self._attr_brightness > brightness:
                await self._async_brightness_down()
                # Break if we've reached or gone below the target
                if self._attr_brightness <= brightness:
                    break

        self.async_write_ha_state()

    async def _async_brightness_up(self):
        """Increase brightness by one step."""
        await self.send_command("brightnessUp")
        # Increase internal brightness state
        new_brightness = min(255, self._attr_brightness + self.BRIGHTNESS_STEP)
        self._attr_brightness = new_brightness
        return True

    async def _async_brightness_down(self):
        """Decrease brightness by one step."""
        await self.send_command("brightnessDown")
        # Decrease internal brightness state
        new_brightness = max(1, self._attr_brightness - self.BRIGHTNESS_STEP)
        self._attr_brightness = new_brightness
        return True

    @callback
    def _async_update_power(self, state) -> None:
        """
        Update the current on/off state based on the power sensor's reading.

        This is relevant if you have a power sensor to reflect the actual device state.
        """
        try:
            if state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE) and state.state != self._state:
                self._state = STATE_ON if state.state == STATE_ON else STATE_OFF
                self.async_write_ha_state()
        except ValueError as ex:
            _LOGGER.error("Unable to update from power sensor: %s", ex)

    async def _async_power_sensor_changed(self, event: Event) -> None:
        """
        Respond to state changes of the power sensor.
        """
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        self._async_update_power(new_state)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    """
    Set up SwitchBotRemoteLight entities from the config entry.

    Args:
        hass (HomeAssistant): Home Assistant instance
        entry (ConfigEntry): The integration config entry
        async_add_entities (function): Callable to add new entities
    """
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]

    # Filter only remotes that match IR_LIGHT_TYPES
    entities = [
        SwitchBotRemoteLight(hass, remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_LIGHT_TYPES, remotes)
    ]

    async_add_entities(entities)
    return True
