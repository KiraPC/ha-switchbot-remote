from typing import List
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,  # v2022.5
    STATE_DOCKED,
    STATE_CLEANING,
    STATE_IDLE,
    STATE_IDLE,
    STATE_RETURNING
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from .client.remote import SupportedRemote

from .const import DOMAIN, IR_VACUUM_TYPES, VACUUM_CLASS


class SwitchBotRemoteVacuum(StateVacuumEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, options: dict = {}):
        super().__init__()
        self.sb = sb
        self._hass = hass
        self._unique_id = sb.id
        self._device_name = sb.name
        self._state = STATE_IDLE

        self._supported_features = VacuumEntityFeature.STATE | VacuumEntityFeature.START | VacuumEntityFeature.STOP | VacuumEntityFeature.RETURN_HOME

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer="SwitchBot",
            name=self._device_name,
            model=VACUUM_CLASS + " Remote",
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the display name of this vacuum."""
        return self._device_name

    @property
    def state(self) -> str | None:
        return self._state

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._supported_features

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._state = last_state.state

    async def async_start(self):
        """Send the power on command."""
        await self.send_command("turnOn")
        self._state = STATE_CLEANING

    async def async_stop(self):
        """Send the power off command."""
        await self.send_command("turnOff")
        self._state = STATE_IDLE

    async def async_return_to_base(self):
        """Send the power off command."""
        await self.send_command("CHARGE", None, True)
        self._state = STATE_IDLE


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    remotes: List[SupportedRemote] = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SwitchBotRemoteVacuum(hass, remote, entry.data.get(remote.id, {}))
        for remote in filter(lambda r: r.type in IR_VACUUM_TYPES, remotes)
    ]

    async_add_entities(entities)

    return True
