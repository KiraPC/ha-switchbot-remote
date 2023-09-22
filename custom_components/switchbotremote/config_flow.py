"""Config flow for SwitchBot Remote IR integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from .client import SwitchBot

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("token"): str,
        vol.Required("secret"): str,
    }
)

STEP_CONFIGURE_BY_DEVICE_TYPE = {
    "DIY Air Conditioner": "Air Conditioner",
    "Air Conditioner": "Air Conditioner",
    
	"DIY Fan": "Fan",
    "Fan": "Fan",
    
	"DIY Light": "Light",
    "Light": "Light",
    
	"DIY TV": "Media",
    "TV": "Media",
    "DIY IPTV": "Media",
    "IPTV": "Media",
    "DIY DVD": "Media",
    "DVD": "Media",
    "DIY Speaker": "Media",
    "Speaker": "Media",
    "DIY Set Top Box": "Media",
    "Set Top Box": "Media",
}

STEP_CONFIGURE_DEVICE = {
    "Air Conditioner": lambda x: vol.Schema({
        vol.Optional("temperature_sensor", default=x.get("temperature_sensor")): str,
        vol.Optional("umidity_sensor", default=x.get("umidity_sensor")): str,
    }),
    "Media": lambda x: vol.Schema({
        vol.Optional("power_sensor", default=x.get("power_sensor")): str,
    }),
    "Fan": lambda x: vol.Schema({
        vol.Optional("power_sensor", default=x.get("power_sensor")): str,
    }),
    "Light": lambda x: vol.Schema({
        vol.Optional("power_sensor", default=x.get("power_sensor")): str,
    })
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
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
    """Handle options flow for LocalTuya integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize localtuya options flow."""
        self.config_entry = config_entry
        # self.dps_strings = config_entry.data.get(CONF_DPS_STRINGS, gen_dps_strings())
        # self.entities = config_entry.data[CONF_ENTITIES]
        self.data = config_entry.data
        self.sb = SwitchBot(token=self.data["token"], secret=self.data["secret"])
        self.discovered_devices = []
        self.selected_device = None

        self.entities = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
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

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("selected_device"): vol.In(devices)})
        )

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
            if remote.id == self.selected_device and remote.type in STEP_CONFIGURE_BY_DEVICE_TYPE:
                schema = STEP_CONFIGURE_DEVICE[STEP_CONFIGURE_BY_DEVICE_TYPE[remote.type]](
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
