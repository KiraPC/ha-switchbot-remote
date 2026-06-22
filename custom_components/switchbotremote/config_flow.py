"""Config flow for SwitchBot Remote IR integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.climate.const import HVACMode
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.selector import selector

from .client import SwitchBot, switchbot_host
from .const import (
    AIR_CONDITIONER_CLASS,
    CAMERA_CLASS,
    CLASS_BY_TYPE,
    CONF_CUSTOMIZE_COMMANDS,
    CONF_HUMIDITY_SENSOR,
    CONF_HVAC_MODES,
    CONF_OFF_COMMAND,
    CONF_ON_COMMAND,
    CONF_OVERRIDE_OFF_COMMAND,
    CONF_POWER_SENSOR,
    CONF_TEMP_MAX,
    CONF_TEMP_MIN,
    CONF_TEMP_STEP,
    CONF_TEMPERATURE_SENSOR,
    CONF_WITH_BRIGHTNESS,
    CONF_WITH_ION,
    CONF_WITH_SPEED,
    CONF_WITH_SWING,
    CONF_WITH_TEMPERATURE,
    CONF_WITH_TIMER,
    DOMAIN,
    FAN_CLASS,
    LIGHT_CLASS,
    MEDIA_CLASS,
    OTHERS_CLASS,
    VACUUM_CLASS,
    WATER_HEATER_CLASS,
    MEDIA_PLAYER_COMMANDS,
)

# Generar opciones para comandos extra basados en MEDIA_PLAYER_COMMANDS
MEDIA_EXTRA_COMMANDS = {
    device_type: [
        {"label": command.replace('_', ' ').capitalize(), "value": command}
        for command in commands.get("extra", {}).keys()
    ]
    for device_type, commands in MEDIA_PLAYER_COMMANDS.items()
}

DEFAULT_HVAC_MODES = [
    HVACMode.AUTO,
    HVACMode.COOL,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.HEAT,
    HVACMode.OFF,
]

HVAC_MODES = [
    {"label": "Auto", "value": str(HVACMode.AUTO)},
    {"label": "Cool", "value": str(HVACMode.COOL)},
    {"label": "Dry", "value": str(HVACMode.DRY)},
    {"label": "Fan Only", "value": str(HVACMode.FAN_ONLY)},
    {"label": "Heat", "value": str(HVACMode.HEAT)},
    {"label": "Off", "value": str(HVACMode.OFF)},
]

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host", default=switchbot_host): str,
        vol.Required("name"): str,
        vol.Required("token"): str,
        vol.Required("secret"): str,
    }
)

STEP_CONFIGURE_DEVICE = {
    AIR_CONDITIONER_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_TEMPERATURE_SENSOR, description={"suggested_value": x.get(CONF_TEMPERATURE_SENSOR)}): selector({"entity": {"filter": {"domain": "sensor"}}}),
        vol.Optional(CONF_HUMIDITY_SENSOR, description={"suggested_value": x.get(CONF_HUMIDITY_SENSOR)}): selector({"entity": {"filter": {"domain": "sensor"}}}),
        vol.Optional(CONF_OVERRIDE_OFF_COMMAND, default=x.get(CONF_OVERRIDE_OFF_COMMAND, True)): bool,
        vol.Optional(CONF_TEMP_MIN, default=x.get(CONF_TEMP_MIN, 16)): int,
        vol.Optional(CONF_TEMP_MAX, default=x.get(CONF_TEMP_MAX, 30)): int,
        vol.Optional(CONF_TEMP_STEP, default=x.get(CONF_TEMP_STEP, 1.0)): selector({"number": {"min": 1.0, "max": 5.0, "step": 1.0, "mode": "slider"}}),
        vol.Optional(CONF_HVAC_MODES, description={"suggested_value": x.get(CONF_HVAC_MODES, DEFAULT_HVAC_MODES)}): vol.All(selector({"select": {"multiple": True, "options": HVAC_MODES}})),
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    MEDIA_CLASS: lambda x, device_type=None: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({
            "select": {
                "multiple": True,
                "custom_value": True,
                "options": MEDIA_EXTRA_COMMANDS.get(device_type.replace("DIY ", ""), []) if device_type else []
            }
        }),
    }),
    FAN_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_WITH_SPEED, default=x.get(CONF_WITH_SPEED, False)): bool,
        vol.Optional(CONF_WITH_ION, default=x.get(CONF_WITH_ION, False)): bool,
        vol.Optional(CONF_WITH_TIMER, default=x.get(CONF_WITH_TIMER, False)): bool,
        vol.Optional(CONF_WITH_SWING, default=x.get(CONF_WITH_SWING, False)): bool,
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    LIGHT_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_WITH_BRIGHTNESS, default=x.get(CONF_WITH_BRIGHTNESS, False)): bool,
        vol.Optional(CONF_WITH_TEMPERATURE, default=x.get(CONF_WITH_TEMPERATURE, False)): bool,
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    CAMERA_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    VACUUM_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    WATER_HEATER_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_TEMPERATURE_SENSOR, description={"suggested_value": x.get(CONF_TEMPERATURE_SENSOR)}): selector({"entity": {"filter": {"domain": "sensor"}}}),
        vol.Optional(CONF_TEMP_MIN, default=x.get(CONF_TEMP_MIN, 40)): int,
        vol.Optional(CONF_TEMP_MAX, default=x.get(CONF_TEMP_MAX, 65)): int,
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    OTHERS_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_ON_COMMAND, default=x.get(CONF_ON_COMMAND, "")): str,
        vol.Optional(CONF_OFF_COMMAND, default=x.get(CONF_OFF_COMMAND, "")): str,
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
}


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    switchbot = SwitchBot(
        token=data["token"],
        secret=data["secret"],
        host=data.get("host", switchbot_host)
    )

    try:
        remotes = await hass.async_add_executor_job(switchbot.remotes)
        _LOGGER.debug(f"Found remotes: {remotes}")
        return {"title": data["name"], "remotes": remotes}
    except Exception as exception:
        raise ConfigEntryAuthFailed from exception


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SwitchBot Remote IR."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(_config_entry):
        """Get options flow for this handler."""
        return OptionsFlowHandler()

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = user_input["name"]
            uniq_id = f"switchbot_remote_{name}"
            await self.async_set_unique_id(uniq_id)
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )

        old_entry = self._get_reconfigure_entry()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required("host", default=old_entry.data.get('host', switchbot_host)): str,
                    vol.Required("name", default=old_entry.data['name']): str,
                    vol.Required("token", default=old_entry.data['token']): str,
                    vol.Required("secret", default=old_entry.data['secret']): str,
                }
            )
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                name = info["title"]
                uniq_id = f"switchbot_remote_{name}"
                await self.async_set_unique_id(uniq_id)
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SwitchBot integration."""

    def __init__(self) -> None:
        """Initialize SwitchBot options flow."""
        self.discovered_devices = []
        self.selected_device = None
        self.current_device_type = None
        self.entities = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.selected_device = user_input["selected_device"]
            for remote in self.discovered_devices:
                if remote.id == self.selected_device:
                    self.current_device_type = remote.type
                    break
            _LOGGER.debug(f"Selected device: {self.selected_device}, Type: {self.current_device_type}")
            return await self.async_step_edit_device()

        data = self.config_entry.data
        sb = SwitchBot(
            token=data["token"],
            secret=data["secret"],
            host=data.get("host", switchbot_host)
        )
        try:
            self.discovered_devices = await self.hass.async_add_executor_job(sb.remotes)
            _LOGGER.debug(f"Discovered devices: {self.discovered_devices}")
        except Exception as exception:
            _LOGGER.error(f"Failed to discover devices: {exception}")
            raise ConfigEntryAuthFailed from exception

        devices = dict()
        for remote in self.discovered_devices:
            devices[remote.id] = remote.name

        return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Required("selected_device"): vol.In(devices)}))

    async def async_step_edit_device(self, user_input=None):
        """Handle editing a device."""
        if user_input is not None:
            #_LOGGER.debug(f"Saving config for device {self.selected_device}: {user_input}")
            new_data = self.config_entry.data.copy()
            new_data[self.selected_device] = user_input
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            _LOGGER.debug(f"Updated config_entry.data: {self.config_entry.data}")
            self.current_device_type = None
            self.selected_device = None
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_abort(reason="device_configured")

        schema = vol.Schema({})
        for remote in self.discovered_devices:
            if remote.id == self.selected_device:
                # _LOGGER.debug(f"Device ID: {remote.id}, Type: {remote.type}")
                config = self.config_entry.data.get(remote.id, {})
                # _LOGGER.debug(f"Loaded config for device {remote.id}: {config}")
                if remote.type in CLASS_BY_TYPE:
                    device_class = CLASS_BY_TYPE[remote.type]
                    # _LOGGER.debug(f"Mapped to class: {device_class}")
                    if device_class == MEDIA_CLASS:
                        options = MEDIA_EXTRA_COMMANDS.get(remote.type.replace("DIY ", ""), [])
                        # _LOGGER.debug(f"Customize commands options for {remote.type}: {options}")
                        # Asegurarse de que los comandos personalizados existentes se muestren
                        current_commands = config.get(CONF_CUSTOMIZE_COMMANDS, [])
                        # _LOGGER.debug(f"Current customize commands for {remote.id}: {current_commands}")
                        schema = STEP_CONFIGURE_DEVICE[device_class](config, device_type=remote.type)
                    else:
                        # _LOGGER.debug(f"Customize commands options for {remote.type}: [] (default for non-MEDIA_CLASS)")
                        current_commands = config.get(CONF_CUSTOMIZE_COMMANDS, [])
                        # _LOGGER.debug(f"Current customize commands for {remote.id}: {current_commands}")
                        schema = STEP_CONFIGURE_DEVICE[device_class](config)
                else:
                    _LOGGER.warning(f"Device type {remote.type} not in CLASS_BY_TYPE, defaulting to OTHERS_CLASS")
                    current_commands = config.get(CONF_CUSTOMIZE_COMMANDS, [])
                    _LOGGER.debug(f"Current customize commands for {remote.id}: {current_commands}")
                    schema = STEP_CONFIGURE_DEVICE[OTHERS_CLASS](config)

        #_LOGGER.debug(f"Generated schema for device {remote.id}: {schema}")
        return self.async_show_form(
            step_id="edit_device",
            data_schema=schema
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
