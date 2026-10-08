"""Zentrale Verwaltung: Standorte, Pflanzen und persistente Speicherung."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store

from .const import (
    CONF_AREA,
    CONF_FLOWER_WEEKS,
    CONF_LOCATION_TYPE,
    CONF_MOTHER,
    CONF_MOTHER_NAME,
    CONF_PHENOTYPE,
    CONF_STRAIN,
    DOMAIN,
    LOCATION_TYPE_OTHER,
    LOCATION_TYPE_PROPAGATION,
    SIGNAL_PANEL_UPDATE,
    SIGNAL_UPDATE,
    STORAGE_KEY,
    STORAGE_VERSION,
    SUBENTRY_LOCATION,
    SUBENTRY_PLANT,
)
from .plant import GrowPlant

# Felder, die von der Mutter an ihre Stecklinge weitergegeben werden
PROPAGATED_FIELDS = (CONF_STRAIN, CONF_PHENOTYPE, CONF_FLOWER_WEEKS)


@callback
def async_propagate_to_cuttings(
    hass: HomeAssistant,
    entry: ConfigEntry,
    mother_id: str,
    old_title: str,
    old_data: dict[str, Any],
    new_title: str,
    new_data: dict[str, Any],
) -> int:
    """Geänderte Stammdaten einer Mutter an ihre Stecklinge (rekursiv) weitergeben.

    Ein Feld wird nur übernommen, wenn der Steckling noch den alten Wert der Mutter
    hat (geerbt) – individuell geänderte Werte bleiben erhalten. Automatisch
    benannte Stecklinge ("<Mutter> #n") werden mit umbenannt.
    Gibt die Anzahl geänderter Stecklinge zurück.
    """
    changed = 0
    for child in list(entry.subentries.values()):
        if child.subentry_type != SUBENTRY_PLANT or child.data.get(CONF_MOTHER) != mother_id:
            continue

        data = dict(child.data)
        for key in PROPAGATED_FIELDS:
            old, new = old_data.get(key), new_data.get(key)
            if old == new or data.get(key) not in (old, None):
                continue
            if new is None:
                data.pop(key, None)
            else:
                data[key] = new
        data[CONF_MOTHER_NAME] = new_title

        title = child.title
        if new_title != old_title:
            if title == old_title:
                title = new_title
            elif title.startswith(f"{old_title} #"):
                title = new_title + title[len(old_title) :]

        if data == dict(child.data) and title == child.title:
            continue
        # Erst die Stecklinge des Stecklings (mit dessen alten Werten), dann ihn selbst
        changed += async_propagate_to_cuttings(
            hass, entry, child.subentry_id, child.title, dict(child.data), title, data
        )
        hass.config_entries.async_update_subentry(entry, child, data=data, title=title)
        changed += 1
    return changed


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
        async_dispatcher_send(self.hass, SIGNAL_PANEL_UPDATE)

    @callback
    def async_start_midnight_updates(self) -> None:
        """Tageszähler aller Entities und des Panels um Mitternacht aktualisieren."""

        @callback
        def _midnight(_now: datetime) -> None:
            self.async_notify()

        self.entry.async_on_unload(
            async_track_time_change(self.hass, _midnight, hour=0, minute=0, second=5)
        )

    async def async_remove(self) -> None:
        await self._store.async_remove()

    async def async_handle_removed_plants(self) -> None:
        """Vor dem Reload: gelöschte Stecklinge aus dem Protokoll ihrer Mutter austragen.

        Nur hier sind die alten Pflanzen-Objekte (mit Mutter und Schnittdatum) noch bekannt.
        """
        current = self.entry.subentries
        changed = False
        for plant_id, plant in self.plants.items():
            if plant_id in current or not plant.logged_cutting:
                continue
            mother = self.plants.get(plant.mother_id or "")
            if mother is None or mother.subentry_id not in current:
                continue
            changed |= mother.remove_logged_cutting(plant.grow_start)
        if changed:
            await self.async_save()

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
        device = self.async_get_device(subentry_id)
        if device is not None and device.area_id != area_id:
            dr.async_get(self.hass).async_update_device(device.id, area_id=area_id)

    @callback
    def async_get_device(self, subentry_id: str) -> dr.DeviceEntry | None:
        """Gerät eines Standorts/einer Pflanze innerhalb dieses Config Entries finden.

        Ersetzt DeviceRegistry.async_get_device (veraltet ab HA 2027.8): Kennungen sind
        nur noch pro Config Entry eindeutig. async_entries_for_config_entry gibt es in
        allen unterstützten HA-Versionen.
        """
        identifier = (DOMAIN, subentry_id)
        for device in dr.async_entries_for_config_entry(dr.async_get(self.hass), self.entry.entry_id):
            if identifier in device.identifiers:
                return device
        return None
