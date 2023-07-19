"""The SwitchBot Remote IR integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .client import SwitchBot

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.MEDIA_PLAYER, Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SwitchBot Remote IR from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    entry.add_update_listener(update_listener)

    switchbot = SwitchBot(token=entry.data["token"], secret=entry.data["secret"])
    remotes = await hass.async_add_executor_job(switchbot.remotes)
    hass.data[DOMAIN][entry.entry_id] = remotes

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
