import humps, logging
from typing import List
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from .client.remote import SupportedRemote

from .const import (
    DOMAIN,
    IR_CAMERA_TYPES,
    IR_FAN_TYPES,
    IR_LIGHT_TYPES,
    CLASS_BY_TYPE,
    CONF_CUSTOMIZE_COMMANDS,
    CONF_WITH_ION,
    CONF_WITH_TIMER,
    CONF_WITH_BRIGHTNESS,
    CONF_WITH_TEMPERATURE,
)

_LOGGER = logging.getLogger(__name__)


class SwitchBotRemoteButton(ButtonEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, command_name: str, command_icon: str) -> None:
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._command_name = command_name
        self._command_icon = command_icon

    def __repr__(self):
        return f"SwitchBotRemoteButton(command={self._command_name}&device={self.device_info})"

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=CLASS_BY_TYPE[self.sb.type] + " Remote",
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id + "_" + humps.decamelize(self._command_name)

    @property
    def name(self) -> str:
        """Return the display name of this button."""
        return self._device_name + " " + self._command_name.capitalize()

    @property
    def icon(self) -> str:
        """Return the icon of this button."""
        return self._command_icon

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.send_command(self._command_name, None, True)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for remote in remotes:
        options = entry.data.get(remote.id, {})
        customize_commands = options.get(CONF_CUSTOMIZE_COMMANDS, [])

        if (remote.type in IR_CAMERA_TYPES):
            entities.append(SwitchBotRemoteButton(
                hass, remote, "SHUTTER", "mdi:camera-iris"))
            entities.append(SwitchBotRemoteButton(
                hass, remote, "MENU", "mdi:menu"))
            entities.append(SwitchBotRemoteButton(
                hass, remote, "TIMER", "mdi:timer"))

        if (remote.type in IR_FAN_TYPES):
            if (options.get(CONF_WITH_ION, False)):
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "ION", "mdi:air-filter"))
            if (options.get(CONF_WITH_TIMER, False)):
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "TIMER", "mdi:timer"))

        if (remote.type in IR_LIGHT_TYPES):
            if (options.get(CONF_WITH_BRIGHTNESS, False)):
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "DARKER", "mdi:brightness-4"))
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "BRIGHTER", "mdi:brightness-6"))

            if (options.get(CONF_WITH_TEMPERATURE, False)):
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "WARM", "mdi:octagram-minus"))
                entities.append(SwitchBotRemoteButton(
                    hass, remote, "WHITE", "mdi:octagram-plus"))

        for command in customize_commands:
            if (command and command.strip()):
                entities.append(SwitchBotRemoteButton(
                    hass, remote, command, "mdi:remote"))


    _LOGGER.debug(f'Adding buttons {entities}')
    async_add_entities(entities)

    return True
