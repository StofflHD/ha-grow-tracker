"""Eine Pflanze: Phasen, Standorte, Notizen und Stecklinge."""

from __future__ import annotations

from datetime import date, timedelta
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from homeassistant.components.logbook import async_log_entry
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from .const import (
    CONF_FLOWER_WEEKS,
    CONF_LOCATION,
    CONF_MOTHER,
    CONF_MOTHER_NAME,
    CONF_PHASE,
    CONF_START_DATE,
    CONF_STRAIN,
    DEFAULT_FLOWER_WEEKS,
    DOMAIN,
    EVENT_CUTTINGS_TAKEN,
    EVENT_LOCATION_CHANGED,
    EVENT_NOTE_ADDED,
    EVENT_PHASE_CHANGED,
    MAX_NOTES,
    PHASE_FLOWERING,
    PHASE_GERMINATION,
    PHASE_MOTHER,
    PHASE_ROOTING,
    PHASES,
    SUBENTRY_PLANT,
)

if TYPE_CHECKING:
    from .hub import GrowHub, GrowLocation


class GrowPlant:
    def __init__(
        self, hub: GrowHub, subentry: ConfigSubentry, data: dict[str, Any] | None
    ) -> None:
        self.hub = hub
        self.hass = hub.hass
        self.subentry = subentry
        self.subentry_id = subentry.subentry_id
        self.phase_entity_id: str | None = None
        self.location_entity_id: str | None = None
        self.data: dict[str, Any] = data or self._initial_data()
        self.data.setdefault("notes", [])
        self.data.setdefault("cuttings", [])
        self.data.setdefault("locations", [])

    def _initial_data(self) -> dict[str, Any]:
        cfg = self.subentry.data
        start = cfg.get(CONF_START_DATE) or _today().isoformat()
        phase = cfg.get(CONF_PHASE) or (
            PHASE_ROOTING if cfg.get(CONF_MOTHER) else PHASE_GERMINATION
        )
        locations = []
        if cfg.get(CONF_LOCATION):
            locations.append({"location": cfg[CONF_LOCATION], "start": start})
        return {
            "history": [{"phase": phase, "start": start}],
            "locations": locations,
            "notes": [],
            "cuttings": [],
        }

    # --- Konfiguration ---------------------------------------------------

    @property
    def name(self) -> str:
        return self.subentry.title

    @property
    def strain(self) -> str | None:
        return self.subentry.data.get(CONF_STRAIN) or None

    @property
    def flower_weeks(self) -> int:
        return int(self.subentry.data.get(CONF_FLOWER_WEEKS, DEFAULT_FLOWER_WEEKS))

    # --- Mutter / Stecklinge --------------------------------------------

    @property
    def mother_id(self) -> str | None:
        return self.subentry.data.get(CONF_MOTHER)

    @property
    def mother_name(self) -> str | None:
        if not self.mother_id:
            return None
        mother = self.hub.plants.get(self.mother_id)
        return mother.name if mother else self.subentry.data.get(CONF_MOTHER_NAME)

    @property
    def origin(self) -> str:
        return "cutting" if self.mother_id else "seed"

    @property
    def cuttings_log(self) -> list[dict[str, Any]]:
        return self.data["cuttings"]

    @property
    def cuttings_taken(self) -> int:
        return sum(item["count"] for item in self.cuttings_log)

    def children(self) -> list[GrowPlant]:
        return [p for p in self.hub.plants.values() if p.mother_id == self.subentry_id]

    # --- Phasen ----------------------------------------------------------

    @property
    def history(self) -> list[dict[str, str]]:
        return self.data["history"]

    @property
    def phase(self) -> str:
        return self.history[-1]["phase"]

    @property
    def phase_start(self) -> date:
        return date.fromisoformat(self.history[-1]["start"])

    @property
    def grow_start(self) -> date:
        return date.fromisoformat(self.history[0]["start"])

    @property
    def days_total(self) -> int:
        return max((_today() - self.grow_start).days, 0)

    @property
    def days_in_phase(self) -> int:
        return max((_today() - self.phase_start).days, 0)

    @property
    def week_in_phase(self) -> int:
        return self.days_in_phase // 7 + 1

    @property
    def expected_harvest(self) -> date | None:
        if self.phase != PHASE_FLOWERING:
            return None
        return self.phase_start + timedelta(weeks=self.flower_weeks)

    def phase_durations(self) -> dict[str, int]:
        return _durations(self.history, "phase")

    # --- Standort --------------------------------------------------------

    @property
    def location_history(self) -> list[dict[str, str]]:
        return self.data["locations"]

    @property
    def location_id(self) -> str | None:
        return self.location_history[-1]["location"] if self.location_history else None

    @property
    def location(self) -> GrowLocation | None:
        return self.hub.locations.get(self.location_id) if self.location_id else None

    @property
    def location_name(self) -> str | None:
        return self.location.name if self.location else None

    @property
    def location_start(self) -> date:
        if not self.location_history:
            return self.grow_start
        return date.fromisoformat(self.location_history[-1]["start"])

    @property
    def days_at_location(self) -> int:
        return max((_today() - self.location_start).days, 0)

    def location_history_named(self) -> list[dict[str, str]]:
        """Standort-Historie mit Namen statt IDs (für Attribute)."""
        return [
            {
                "location": (
                    loc.name
                    if (loc := self.hub.locations.get(item["location"]))
                    else "?"
                ),
                "start": item["start"],
            }
            for item in self.location_history
        ]

    # --- Aktionen --------------------------------------------------------

    async def async_set_phase(self, phase: str, start: date | None = None) -> None:
        if phase not in PHASES:
            raise ServiceValidationError(f"Unbekannte Phase: {phase}")
        if phase == self.phase and start is None:
            return

        old_phase = self.phase
        _apply_change(self.history, "phase", phase, start or _today())

        if phase != old_phase:
            self.hass.bus.async_fire(
                EVENT_PHASE_CHANGED,
                {
                    **self._event_base(),
                    "from_phase": old_phase,
                    "to_phase": phase,
                    "date": self.history[-1]["start"],
                },
            )
        await self.hub.async_save_and_notify()

    async def async_set_location(self, location_id: str, start: date | None = None) -> None:
        if location_id not in self.hub.locations:
            raise ServiceValidationError(f"Unbekannter Standort: {location_id}")
        if location_id == self.location_id and start is None:
            return

        old_name = self.location_name
        _apply_change(self.location_history, "location", location_id, start or _today())

        if old_name != self.location_name:
            self.hass.bus.async_fire(
                EVENT_LOCATION_CHANGED,
                {
                    **self._event_base(),
                    "from_location": old_name,
                    "to_location": self.location_name,
                    "date": self.location_history[-1]["start"],
                },
            )
            self.async_sync_area()
        await self.hub.async_save_and_notify()

    async def async_add_note(self, text: str) -> None:
        note = {
            "date": dt_util.now().isoformat(timespec="minutes"),
            "location": self.location_name,
            "phase": self.phase,
            "day": self.days_total,
            "text": text,
        }
        self.data["notes"].append(note)
        del self.data["notes"][:-MAX_NOTES]

        self.hass.bus.async_fire(EVENT_NOTE_ADDED, {**self._event_base(), **note})
        async_log_entry(self.hass, self.name, text, DOMAIN, self.phase_entity_id)
        await self.hub.async_save_and_notify()

    async def async_take_cuttings(
        self,
        count: int,
        start: date | None = None,
        create_plants: bool = False,
        location_id: str | None = None,
    ) -> None:
        if self.phase != PHASE_MOTHER:
            raise ServiceValidationError(f"{self.name} ist keine Mutterpflanze")
        if location_id is not None and location_id not in self.hub.locations:
            raise ServiceValidationError(f"Unbekannter Standort: {location_id}")

        start = start or _today()
        self.cuttings_log.append({"date": start.isoformat(), "count": count})
        self.hass.bus.async_fire(
            EVENT_CUTTINGS_TAKEN,
            {
                **self._event_base(),
                "count": count,
                "date": start.isoformat(),
                "created_plants": create_plants,
            },
        )
        async_log_entry(
            self.hass, self.name, f"{count} cuttings taken", DOMAIN, self.phase_entity_id
        )
        await self.hub.async_save_and_notify()

        if not create_plants:
            return

        location_id = location_id or self.hub.default_cutting_location(self)
        number = len(self.children())
        entry = self.hub.entry

        # Alle Subentries anlegen, danach genau einmal neu laden
        self.hub.reload_pending = True
        for _ in range(count):
            number += 1
            data: dict[str, Any] = {
                CONF_MOTHER: self.subentry_id,
                CONF_MOTHER_NAME: self.name,
                CONF_PHASE: PHASE_ROOTING,
                CONF_START_DATE: start.isoformat(),
                CONF_FLOWER_WEEKS: self.flower_weeks,
            }
            if location_id:
                data[CONF_LOCATION] = location_id
            if self.strain:
                data[CONF_STRAIN] = self.strain
            self.hass.config_entries.async_add_subentry(
                entry,
                ConfigSubentry(
                    data=MappingProxyType(data),
                    subentry_type=SUBENTRY_PLANT,
                    title=f"{self.name} #{number}",
                    unique_id=None,
                ),
            )
        self.hass.config_entries.async_schedule_reload(entry.entry_id)

    @callback
    def async_sync_area(self) -> None:
        if self.location is not None:
            self.hub.async_set_device_area(self.subentry_id, self.location.area_id)

    def _event_base(self) -> dict[str, Any]:
        return {"plant": self.name, "plant_id": self.subentry_id}


def _apply_change(
    history: list[dict[str, str]], key: str, value: str, start: date
) -> None:
    """Neuen Eintrag anhängen oder Startdatum des aktuellen Eintrags korrigieren."""
    if history and history[-1][key] == value:
        if len(history) > 1 and start < date.fromisoformat(history[-2]["start"]):
            raise ServiceValidationError("Datum liegt vor dem vorherigen Eintrag")
        history[-1]["start"] = start.isoformat()
        return
    if history and start < date.fromisoformat(history[-1]["start"]):
        raise ServiceValidationError("Datum liegt vor dem aktuellen Eintrag")
    history.append({key: value, "start": start.isoformat()})


def _durations(history: list[dict[str, str]], key: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for idx, item in enumerate(history):
        start = date.fromisoformat(item["start"])
        end = (
            date.fromisoformat(history[idx + 1]["start"])
            if idx + 1 < len(history)
            else _today()
        )
        result[item[key]] = result.get(item[key], 0) + max((end - start).days, 0)
    return result


def _today() -> date:
    return dt_util.now().date()
