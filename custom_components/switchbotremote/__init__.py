"""The SwitchBot Remote IR integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .client import SwitchBot

from .const import DOMAIN
from homeassistant.helpers import (
    device_registry as dr,
)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.MEDIA_PLAYER,
    Platform.LIGHT,
    Platform.FAN,
    Platform.BUTTON,
    Platform.VACUUM,
    Platform.REMOTE,
    Platform.WATER_HEATER,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SwitchBot Remote IR from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    entry.add_update_listener(update_listener)

    switchbot = SwitchBot(token=entry.data["token"], secret=entry.data["secret"])
    remotes = await hass.async_add_executor_job(switchbot.remotes)

    _LOGGER.debug(f"Configuring remotes: {remotes}")
    hass.data[DOMAIN][entry.entry_id] = remotes

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    device_registry = dr.async_get(hass)
    for device_entry in dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    ):
        device_id = list(device_entry.identifiers)[0][1]
        registered = next((remote for remote in remotes if remote.id == device_id), None)

        if not registered:
            device_registry.async_remove_device(device_entry.id)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
