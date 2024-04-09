"""Config flow for SwitchBot Remote IR integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector
from homeassistant.components.climate.const import HVACMode
from homeassistant.exceptions import ConfigEntryAuthFailed
from .client import SwitchBot

from .const import (
    DOMAIN,
    CLASS_BY_TYPE,

    AIR_CONDITIONER_CLASS,
    FAN_CLASS,
    LIGHT_CLASS,
    MEDIA_CLASS,
    CAMERA_CLASS,
    VACUUM_CLASS,
    WATER_HEATER_CLASS,
    OTHERS_CLASS,

    CONF_POWER_SENSOR,
    CONF_TEMPERATURE_SENSOR,
    CONF_HUMIDITY_SENSOR,
    CONF_TEMP_MIN,
    CONF_TEMP_MAX,
    CONF_TEMP_STEP,
    CONF_HVAC_MODES,
    CONF_CUSTOMIZE_COMMANDS,
    CONF_WITH_SPEED,
    CONF_WITH_ION,
    CONF_WITH_TIMER,
    CONF_WITH_BRIGHTNESS,
    CONF_WITH_TEMPERATURE,
    CONF_ON_COMMAND,
    CONF_OFF_COMMAND,
    CONF_OVERRIDE_OFF_COMMAND,
)

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
        vol.Optional(CONF_TEMP_STEP, default=x.get(CONF_TEMP_STEP, 1.0)): selector({"number": {"min": 0.1, "max": 2.0, "step": 0.1, "mode": "slider"}}),
        vol.Optional(CONF_HVAC_MODES, description={"suggested_value": x.get(CONF_HVAC_MODES, DEFAULT_HVAC_MODES)}): vol.All(selector({"select": {"multiple": True, "options": HVAC_MODES}})),
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    MEDIA_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_CUSTOMIZE_COMMANDS, default=x.get(CONF_CUSTOMIZE_COMMANDS, [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    FAN_CLASS: lambda x: vol.Schema({
        vol.Optional(CONF_POWER_SENSOR, description={"suggested_value": x.get(CONF_POWER_SENSOR)}): selector({"entity": {"filter": {"domain": ["binary_sensor", "input_boolean", "light", "sensor", "switch"]}}}),
        vol.Optional(CONF_WITH_SPEED, default=x.get(CONF_WITH_SPEED, False)): bool,
        vol.Optional(CONF_WITH_ION, default=x.get(CONF_WITH_ION, False)): bool,
        vol.Optional(CONF_WITH_TIMER, default=x.get(CONF_WITH_TIMER, False)): bool,
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
    switchbot = SwitchBot(token=data["token"], secret=data["secret"])

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
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return OptionsFlowHandler(config_entry)

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

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize SwitchBot options flow."""
        self.config_entry = config_entry

        self.data = config_entry.data
        self.sb = SwitchBot(
            token=self.data["token"], secret=self.data["secret"])
        self.discovered_devices = []
        self.selected_device = None

        self.entities = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.selected_device = user_input["selected_device"]
            return await self.async_step_edit_device()

        try:
            self.discovered_devices = await self.hass.async_add_executor_job(self.sb.remotes)
        except Exception as exception:
            raise ConfigEntryAuthFailed from exception

        devices = dict()
        for remote in self.discovered_devices:
            devices[remote.id] = remote.name

        return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Required("selected_device"): vol.In(devices)}))

    async def async_step_edit_device(self, user_input=None):
        """Handle editing a device."""
        if user_input is not None:
            new_data = self.config_entry.data.copy()
            new_data[self.selected_device] = user_input
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            return self.async_create_entry(title=self.data["name"], data=user_input)

        schema = vol.Schema({})
        for remote in self.discovered_devices:
            if remote.id == self.selected_device and remote.type in CLASS_BY_TYPE:
                config = self.config_entry.data.get(remote.id, {})
                schema = STEP_CONFIGURE_DEVICE[CLASS_BY_TYPE[remote.type]](
                    config)

        return self.async_show_form(
            step_id="edit_device",
            data_schema=schema
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
