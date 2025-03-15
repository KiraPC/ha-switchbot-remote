import logging
from typing import List
from homeassistant.components.light import (
    LightEntity,
    ColorMode
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

        # Internally track on/off and brightness. Adjust if brightness isn't really supported.
        self._state = STATE_OFF
        self._brightness = None

        self._power_sensor = options.get(CONF_POWER_SENSOR, None)

        # Internally store the set of supported color modes (here, only brightness).
        self._supported_color_modes = {ColorMode.BRIGHTNESS}

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
    def supported_color_modes(self) -> set:
        """
        Return the set of color modes this light entity supports.
        """
        return self._supported_color_modes

    @property
    def color_mode(self) -> str:
        """
        Return the active color mode, which should be one of the supported_color_modes.
        """
        return ColorMode.BRIGHTNESS

    @property
    def brightness(self) -> int | None:
        """
        Return the brightness level of the light (0-255).
        Remove this property if brightness is truly unsupported by the device.
        """
        return self._brightness

    @property
    def is_on(self) -> bool:
        """
        Return True if the light is on, otherwise False.
        """
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

    async def async_turn_on(self, **kwargs) -> None:
        """
        Turn the light on. Sends 'turnOn' to the remote.

        If brightness is passed in kwargs, use it if your device truly supports brightness.
        """
        await self.send_command("turnOn")
        self._state = STATE_ON

        if "brightness" in kwargs:
            self._brightness = kwargs["brightness"]

    async def async_turn_off(self, **kwargs) -> None:
        """
        Turn the light off. Sends 'turnOff' to the remote.
        """
        await self.send_command("turnOff")
        self._state = STATE_OFF

    async def send_command(self, *args) -> None:
        """
        Use the SwitchBot API (in an executor) to send commands to the remote.
        """
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @callback
    def _async_update_power(self, state) -> None:
        """
        Update the current on/off state based on the power sensor's reading.

        This is relevant if you have a power sensor to reflect the actual device state.
        """
        try:
            if state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE) and state.state != self._state:
                self._state = STATE_ON if state.state == STATE_ON else STATE_OFF
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
