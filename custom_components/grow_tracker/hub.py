"""Zentrale Verwaltung: Standorte, Pflanzen und persistente Speicherung."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import (
    CONF_AREA,
    CONF_LOCATION_TYPE,
    DOMAIN,
    LOCATION_TYPE_OTHER,
    LOCATION_TYPE_PROPAGATION,
    SIGNAL_UPDATE,
    STORAGE_KEY,
    STORAGE_VERSION,
    SUBENTRY_LOCATION,
    SUBENTRY_PLANT,
)
from .plant import GrowPlant


class GrowLocation:
    """Ein Anbauort (Schrank, Zelt, Kammer …)."""

    def __init__(self, hub: GrowHub, subentry: ConfigSubentry) -> None:
        self.hub = hub
        self.subentry_id = subentry.subentry_id
        self.name = subentry.title
        self.location_type: str = subentry.data.get(CONF_LOCATION_TYPE, LOCATION_TYPE_OTHER)
        self.area_id: str | None = subentry.data.get(CONF_AREA)

    def plants(self) -> list[GrowPlant]:
        return [p for p in self.hub.plants.values() if p.location_id == self.subentry_id]


class GrowHub:
    """Hält alle Standorte und Pflanzen eines Grow-Tracker-Eintrags."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.locations: dict[str, GrowLocation] = {}
        self.plants: dict[str, GrowPlant] = {}
        # Unterdrückt Reloads, während mehrere Subentries angelegt werden
        self.reload_pending = False

    async def async_load(self) -> None:
        stored = await self._store.async_load() or {}
        plant_data: dict[str, Any] = stored.get("plants", {})

        for subentry in self.entry.subentries.values():
            if subentry.subentry_type == SUBENTRY_LOCATION:
                self.locations[subentry.subentry_id] = GrowLocation(self, subentry)

        for subentry in self.entry.subentries.values():
            if subentry.subentry_type == SUBENTRY_PLANT:
                self.plants[subentry.subentry_id] = GrowPlant(
                    self, subentry, plant_data.get(subentry.subentry_id)
                )

        # Neue Pflanzen speichern, Daten gelöschter Pflanzen verwerfen
        await self.async_save()

    async def async_save(self) -> None:
        await self._store.async_save(
            {"plants": {pid: plant.data for pid, plant in self.plants.items()}}
        )

    async def async_save_and_notify(self) -> None:
        await self.async_save()
        self.async_notify()

    @callback
    def async_notify(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_UPDATE.format(self.entry.entry_id))

    async def async_remove(self) -> None:
        await self._store.async_remove()

    # --- Standorte -------------------------------------------------------

    def resolve_location(self, value: str) -> str:
        """Standort per ID oder Name (Groß-/Kleinschreibung egal) finden."""
        if value in self.locations:
            return value
        wanted = value.strip().casefold()
        for location in self.locations.values():
            if location.name.casefold() == wanted:
                return location.subentry_id
        raise ServiceValidationError(f"Unbekannter Standort: {value}")

    def default_cutting_location(self, mother: GrowPlant) -> str | None:
        """Erster Anzucht-Standort, sonst der Standort der Mutter."""
        for location in self.locations.values():
            if location.location_type == LOCATION_TYPE_PROPAGATION:
                return location.subentry_id
        return mother.location_id

    # --- Bereiche --------------------------------------------------------

    @callback
    def async_sync_areas(self) -> None:
        for location in self.locations.values():
            self.async_set_device_area(location.subentry_id, location.area_id)
        for plant in self.plants.values():
            plant.async_sync_area()

    @callback
    def async_set_device_area(self, subentry_id: str, area_id: str | None) -> None:
        if area_id is None:
            return
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get_device(identifiers={(DOMAIN, subentry_id)})
        if device is not None and device.area_id != area_id:
            dev_reg.async_update_device(device.id, area_id=area_id)
