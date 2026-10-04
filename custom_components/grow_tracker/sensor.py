"""Sensoren für Pflanzen und Standorte."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import GrowConfigEntry
from .entity import LocationEntity, PlantEntity
from .hub import GrowLocation
from .plant import GrowPlant


@dataclass(frozen=True, kw_only=True)
class GrowSensorDescription(SensorEntityDescription):
    value_fn: Callable[[GrowPlant], Any]
    attrs_fn: Callable[[GrowPlant], dict[str, Any]] | None = None


def _harvest_attrs(plant: GrowPlant) -> dict[str, Any]:
    attrs: dict[str, Any] = {"flower_weeks": plant.flower_weeks}
    if (harvest := plant.expected_harvest) is not None:
        attrs["days_remaining"] = (harvest - dt_util.now().date()).days
    return attrs


def _cuttings_attrs(plant: GrowPlant) -> dict[str, Any]:
    return {
        "log": list(reversed(plant.cuttings_log[-20:])),
        "tracked_cuttings": [
            {
                "name": child.name,
                "phase": child.phase,
                "location": child.location_name,
                "days": child.days_total,
            }
            for child in plant.children()
        ],
    }


def _notes_attrs(plant: GrowPlant) -> dict[str, Any]:
    notes = plant.data["notes"]
    return {"notes": list(reversed(notes[-20:])), "count": len(notes)}


PLANT_SENSORS: tuple[GrowSensorDescription, ...] = (
    GrowSensorDescription(
        key="days_total",
        icon="mdi:calendar-range",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda p: p.days_total,
    ),
    GrowSensorDescription(
        key="days_in_phase",
        icon="mdi:calendar-today",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda p: p.days_in_phase,
    ),
    GrowSensorDescription(
        key="week_in_phase",
        icon="mdi:calendar-week",
        value_fn=lambda p: p.week_in_phase,
    ),
    GrowSensorDescription(
        key="days_at_location",
        icon="mdi:map-marker-radius",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda p: p.days_at_location,
    ),
    GrowSensorDescription(
        key="phase_start",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda p: p.phase_start,
    ),
    GrowSensorDescription(
        key="expected_harvest",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:scissors-cutting",
        value_fn=lambda p: p.expected_harvest,
        attrs_fn=_harvest_attrs,
    ),
    GrowSensorDescription(
        key="cuttings_taken",
        icon="mdi:content-cut",
        # TOTAL statt TOTAL_INCREASING: gelöschte Stecklinge verringern den Zähler
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda p: p.cuttings_taken,
        attrs_fn=_cuttings_attrs,
    ),
    GrowSensorDescription(
        key="last_note",
        icon="mdi:notebook-edit",
        value_fn=lambda p: p.data["notes"][-1]["text"][:255] if p.data["notes"] else None,
        attrs_fn=_notes_attrs,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GrowConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    hub = entry.runtime_data
    for location in hub.locations.values():
        async_add_entities(
            [LocationPlantCountSensor(location)],
            config_subentry_id=location.subentry_id,
        )
    for plant in hub.plants.values():
        async_add_entities(
            [GrowPlantSensor(plant, desc) for desc in PLANT_SENSORS],
            config_subentry_id=plant.subentry_id,
        )


class GrowPlantSensor(PlantEntity, SensorEntity):
    entity_description: GrowSensorDescription

    def __init__(self, plant: GrowPlant, description: GrowSensorDescription) -> None:
        super().__init__(plant, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> int | str | date | None:
        return self.entity_description.value_fn(self.plant)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.plant)


class LocationPlantCountSensor(LocationEntity, SensorEntity):
    """Anzahl Pflanzen an einem Standort."""

    _attr_icon = "mdi:sprout"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, location: GrowLocation) -> None:
        super().__init__(location, "plant_count")

    @property
    def native_value(self) -> int:
        return len(self.location.plants())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "location_type": self.location.location_type,
            "plants": [
                {
                    "name": plant.name,
                    "strain": plant.strain,
                    "phase": plant.phase,
                    "days_in_phase": plant.days_in_phase,
                    "days_at_location": plant.days_at_location,
                }
                for plant in self.location.plants()
            ],
        }
