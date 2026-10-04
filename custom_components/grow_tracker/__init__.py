"""Grow Tracker – protokolliert Phasen, Standorte und Stecklinge von Pflanzen."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .hub import GrowHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]

type GrowConfigEntry = ConfigEntry[GrowHub]


async def async_setup_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> bool:
    hub = GrowHub(hass, entry)
    await hub.async_load()
    entry.runtime_data = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hub.async_sync_areas()
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> None:
    await GrowHub(hass, entry).async_remove()


async def async_migrate_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> bool:
    if entry.version == 1:
        _LOGGER.error(
            "Grow Tracker: Einträge aus Version 0.1 werden nicht mehr unterstützt. "
            "Bitte löschen und neu einrichten"
        )
        return False
    return True


async def _async_update_listener(hass: HomeAssistant, entry: GrowConfigEntry) -> None:
    """Neu laden, wenn Standorte/Pflanzen hinzugefügt, geändert oder gelöscht werden."""
    if entry.runtime_data.reload_pending:
        return
    await hass.config_entries.async_reload(entry.entry_id)
