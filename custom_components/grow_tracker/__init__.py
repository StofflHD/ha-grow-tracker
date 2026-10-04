"""Grow Tracker – protokolliert Phasen, Standorte und Stecklinge von Pflanzen."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, SIGNAL_PANEL_UPDATE
from .hub import GrowHub
from .panel import async_register_panel, async_register_static_path, async_remove_panel
from .websocket import async_setup_websocket

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type GrowConfigEntry = ConfigEntry[GrowHub]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Einmalig: Websocket-API und Panel-Dateien bereitstellen."""
    async_setup_websocket(hass)
    await async_register_static_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> bool:
    hub = GrowHub(hass, entry)
    await hub.async_load()
    entry.runtime_data = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hub.async_sync_areas()
    hub.async_start_midnight_updates()
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await async_register_panel(hass)
    async_dispatcher_send(hass, SIGNAL_PANEL_UPDATE)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GrowConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        async_remove_panel(hass)
    return unloaded


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
