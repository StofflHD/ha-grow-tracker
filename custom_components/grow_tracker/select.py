"""Phasen- und Standort-Auswahl pro Pflanze inkl. Entity-Services."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import voluptuous as vol

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GrowConfigEntry
from .const import (
    ATTR_COUNT,
    ATTR_CREATE_PLANTS,
    ATTR_DATE,
    ATTR_LOCATION,
    ATTR_NOTE,
    ATTR_PHASE,
    PHASES,
    SERVICE_ADD_NOTE,
    SERVICE_SET_LOCATION,
    SERVICE_SET_PHASE,
    SERVICE_TAKE_CUTTINGS,
)
from .entity import PlantEntity
from .plant import GrowPlant


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GrowConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    for plant in entry.runtime_data.plants.values():
        async_add_entities(
            [GrowPhaseSelect(plant), GrowLocationSelect(plant)],
            config_subentry_id=plant.subentry_id,
        )

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_PHASE,
        {vol.Required(ATTR_PHASE): vol.In(PHASES), vol.Optional(ATTR_DATE): cv.date},
        "async_service_set_phase",
    )
    platform.async_register_entity_service(
        SERVICE_SET_LOCATION,
        {vol.Required(ATTR_LOCATION): cv.string, vol.Optional(ATTR_DATE): cv.date},
        "async_service_set_location",
    )
    platform.async_register_entity_service(
        SERVICE_ADD_NOTE,
        {vol.Required(ATTR_NOTE): cv.string, vol.Optional(ATTR_DATE): cv.datetime},
        "async_service_add_note",
    )
    platform.async_register_entity_service(
        SERVICE_TAKE_CUTTINGS,
        {
            vol.Required(ATTR_COUNT): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Optional(ATTR_DATE): cv.date,
            vol.Optional(ATTR_CREATE_PLANTS, default=False): cv.boolean,
            vol.Optional(ATTR_LOCATION): cv.string,
        },
        "async_service_take_cuttings",
    )


class GrowSelectBase(PlantEntity, SelectEntity):
    """Dienste funktionieren mit beiden Select-Entities einer Pflanze als Ziel."""

    async def async_service_set_phase(self, phase: str, date: date | None = None) -> None:
        await self.plant.async_set_phase(phase, date)

    async def async_service_set_location(
        self, location: str, date: date | None = None
    ) -> None:
        await self.plant.async_set_location(self.hub.resolve_location(location), date)

    async def async_service_add_note(self, note: str, date: datetime | None = None) -> None:
        await self.plant.async_add_note(note, date)

    async def async_service_take_cuttings(
        self,
        count: int,
        date: date | None = None,
        create_plants: bool = False,
        location: str | None = None,
    ) -> None:
        location_id = self.hub.resolve_location(location) if location else None
        await self.plant.async_take_cuttings(count, date, create_plants, location_id)


class GrowPhaseSelect(GrowSelectBase):
    _attr_options = PHASES
    _attr_icon = "mdi:cannabis"

    def __init__(self, plant: GrowPlant) -> None:
        super().__init__(plant, "phase")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.plant.phase_entity_id = self.entity_id

    @property
    def current_option(self) -> str:
        return self.plant.phase

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "strain": self.plant.strain,
            "phenotype": self.plant.phenotype,
            "origin": self.plant.origin,
            "mother": self.plant.mother_name,
            "location": self.plant.location_name,
            "grow_start": self.plant.grow_start.isoformat(),
            "phase_start": self.plant.phase_start.isoformat(),
            "history": self.plant.history,
            "phase_durations_days": self.plant.phase_durations(),
        }

    async def async_select_option(self, option: str) -> None:
        await self.plant.async_set_phase(option)


class GrowLocationSelect(GrowSelectBase):
    _attr_icon = "mdi:home-floor-a"

    def __init__(self, plant: GrowPlant) -> None:
        super().__init__(plant, "location")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.plant.location_entity_id = self.entity_id

    @property
    def options(self) -> list[str]:
        return [loc.name for loc in self.hub.locations.values()]

    @property
    def current_option(self) -> str | None:
        return self.plant.location_name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "since": self.plant.location_start.isoformat(),
            "days_at_location": self.plant.days_at_location,
            "history": self.plant.location_history_named(),
        }

    async def async_select_option(self, option: str) -> None:
        await self.plant.async_set_location(self.hub.resolve_location(option))
