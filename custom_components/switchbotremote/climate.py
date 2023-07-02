from homeassistant.components.climate import ClimateEntity
from homeassistant.core import HomeAssistant
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from switchbot import Remote

from .const import DOMAIN

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


class SwitchBotRemoteClimate(ClimateEntity):
    _attr_has_entity_name = True

    def __init__(self, sb: Remote, _id: str, name: str) -> None:
        super().__init__()
        self.sb = sb
        self._attr_unique_id = _id
        self._is_on = False
        self._name = name

        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.COOL,
            HVACMode.DRY,
            HVACMode.FAN_ONLY,
            HVACMode.HEAT,
        ]
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_target_temperature = 28
        self._attr_target_temperature_step = 1
        self._attr_fan_mode = FAN_AUTO
        self._attr_fan_modes = [
            FAN_AUTO,
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
        ]

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
        )

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="switchbot",
            name=self._name,
            model="Air Conditioner",
        )

    @property
    def power_state(self):
        return "on" if self._is_on else "off"

    @property
    def target_temperature(self) -> int:
        return self._attr_target_temperature

    def set_temperature(self, **kwargs):
        self._attr_target_temperature = kwargs.get("temperature")

        self._update_remote()

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == "off":
            self.sb.turn("off")
            self._is_on = False

        self._is_on = True
        self._attr_hvac_mode = hvac_mode
        self._update_remote()

    @property
    def fan_mode(self):
        return self._attr_fan_mode

    def set_fan_mode(self, fan_mode):
        self._attr_fan_mode = fan_mode
        self._update_remote()

    def _update_remote(self):
        self.sb.command(
            "setAll",
            f"{self.target_temperature},{HVAC_REMOTE_MODES[self.hvac_mode]},{FAN_REMOTE_MODES[self.fan_mode]},{self.power_state}",
        )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    climates = [
        SwitchBotRemoteClimate(remote, remote.id, remote.name)
        for remote in filter(lambda r: r.type == "Air Conditioner", remotes)
    ]

    async_add_entities(climates)
