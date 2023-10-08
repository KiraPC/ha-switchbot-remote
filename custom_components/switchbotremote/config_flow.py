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
)

DEFAULT_HVAC_MODES = [
    HVACMode.AUTO,
    HVACMode.COOL,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.HEAT,
]

HVAC_MODES = [
    {"label": "Auto", "value": HVACMode.AUTO},
    {"label": "Cool", "value": HVACMode.COOL},
    {"label": "Dry", "value": HVACMode.DRY},
    {"label": "Fan Only", "value": HVACMode.FAN_ONLY},
    {"label": "Heat", "value": HVACMode.HEAT},
]

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("token"): str,
        vol.Required("secret"): str,
    }
)

# TODO: Fix the entity selector default value or empty issue
STEP_CONFIGURE_DEVICE = {
    AIR_CONDITIONER_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        # selector({"entity": {"filter": {"domain": "sensor"}}})
        vol.Optional("temperature_sensor", default=x.get("temperature_sensor", "")): str,
        # selector({"entity": {"filter": {"domain": "sensor"}}})
        vol.Optional("humidity_sensor", default=x.get("humidity_sensor", "")): str,
        vol.Optional("temp_min", default=x.get("temp_min", 16)): int,
        vol.Optional("temp_max", default=x.get("temp_max", 30)): int,
        vol.Optional("temp_step", default=x.get("temp_step", 1.0)): selector({"number": {"min": 0.1, "max": 2.0, "step": 0.1, "mode": "slider"}}),
        vol.Optional("hvac_modes", default=x.get("hvac_modes", DEFAULT_HVAC_MODES)): vol.All(selector({"select": {"multiple": True, "options": HVAC_MODES}})),
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    MEDIA_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    FAN_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        vol.Optional("with_speed", default=x.get("with_speed", False)): bool,
        vol.Optional("with_ion", default=x.get("with_ion", False)): bool,
        vol.Optional("with_timer", default=x.get("with_timer", False)): bool,
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    LIGHT_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        vol.Optional("with_brightness", default=x.get("with_brightness", False)): bool,
        vol.Optional("with_temperature", default=x.get("with_temperature", False)): bool,
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    CAMERA_CLASS: lambda x: vol.Schema({
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    VACUUM_CLASS: lambda x: vol.Schema({
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    WATER_HEATER_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        vol.Optional("temperature_sensor", default=x.get("temperature_sensor", "")): selector({"entity": {"filter": {"domain": "sensor"}}}),
        vol.Optional("temp_min", default=x.get("temp_min", 40)): int,
        vol.Optional("temp_max", default=x.get("temp_max", 65)): int,
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
    OTHERS_CLASS: lambda x: vol.Schema({
        # selector({"entity": {"filter": {"domain": ["binary_sensor","input_boolean","light","sensor","switch"]}}})
        vol.Optional("power_sensor", default=x.get("power_sensor", "")): str,
        vol.Optional("on_command", default=x.get("on_command", "")): str,
        vol.Optional("off_command", default=x.get("off_command", "")): str,
        vol.Optional("customize_commands", default=x.get("customize_commands", [])): selector({"select": {"multiple": True, "custom_value": True, "options": []}}),
    }),
}


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    switchbot = SwitchBot(token=data["token"], secret=data["secret"])

    try:
        remotes = await hass.async_add_executor_job(switchbot.remotes)
        return {"title": data["name"], "remotes": remotes}
    except:
        raise InvalidAuth()


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
        self.sb = SwitchBot(token=self.data["token"], secret=self.data["secret"])
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
        except:
            raise InvalidAuth()

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
                schema = STEP_CONFIGURE_DEVICE[CLASS_BY_TYPE[remote.type]](
                    self.config_entry.data.get(remote.id, {})
                )

        return self.async_show_form(
            step_id="edit_device",
            data_schema=schema
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
