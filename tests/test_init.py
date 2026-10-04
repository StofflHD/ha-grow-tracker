"""Tests für Entities, Dienste, Bereiche und Speicherung."""

from __future__ import annotations

from typing import Any

from freezegun.api import FrozenDateTimeFactory
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

from .conftest import LOC_FLOWER, LOC_MOTHER, LOC_PROP, PLANT_MOTHER, PLANT_SEED


def _eid(hass: HomeAssistant, platform: str, subentry_id: str, key: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{subentry_id}_{key}")
    assert entity_id is not None, f"{platform} {subentry_id}_{key} fehlt"
    return entity_id


def _state(hass: HomeAssistant, platform: str, subentry_id: str, key: str):
    return hass.states.get(_eid(hass, platform, subentry_id, key))


async def _call(hass: HomeAssistant, service: str, subentry_id: str, **data: Any) -> None:
    await hass.services.async_call(
        DOMAIN,
        service,
        {"entity_id": _eid(hass, "select", subentry_id, "phase"), **data},
        blocking=True,
    )
    await hass.async_block_till_done()


async def test_entities(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    assert setup_entry.state is ConfigEntryState.LOADED

    phase = _state(hass, "select", PLANT_SEED, "phase")
    assert phase.state == "germination"
    assert phase.attributes["origin"] == "seed"
    assert phase.attributes["location"] == "Blüte groß"

    location = _state(hass, "select", PLANT_SEED, "location")
    assert location.state == "Blüte groß"
    assert location.attributes["options"] == ["Mutterschrank", "Blüte groß", "Anzucht"]

    assert _state(hass, "sensor", PLANT_SEED, "days_total").state == "14"
    assert _state(hass, "sensor", PLANT_SEED, "week_in_phase").state == "3"
    assert _state(hass, "sensor", PLANT_SEED, "phase_start").state == "2026-09-01"
    assert _state(hass, "sensor", PLANT_SEED, "expected_harvest").state == "unknown"

    assert _state(hass, "sensor", LOC_FLOWER, "plant_count").state == "1"
    assert _state(hass, "sensor", LOC_PROP, "plant_count").state == "0"

    # Ein Gerät pro Standort und Pflanze
    dev_reg = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(dev_reg, setup_entry.entry_id)
    assert len(devices) == 5


async def test_set_phase(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    events = async_capture_events(hass, "grow_tracker_phase_changed")

    await _call(hass, "set_phase", PLANT_SEED, phase="vegetative", date="2026-09-05")
    await _call(hass, "set_phase", PLANT_SEED, phase="flowering")

    phase = _state(hass, "select", PLANT_SEED, "phase")
    assert phase.state == "flowering"
    assert phase.attributes["phase_durations_days"] == {
        "germination": 4,
        "vegetative": 10,
        "flowering": 0,
    }
    assert _state(hass, "sensor", PLANT_SEED, "expected_harvest").state == "2026-11-17"
    harvest = _state(hass, "sensor", PLANT_SEED, "expected_harvest")
    assert harvest.attributes["days_remaining"] == 63

    assert [e.data["to_phase"] for e in events] == ["vegetative", "flowering"]

    # Startdatum der aktuellen Phase korrigieren – kein neues Event
    await _call(hass, "set_phase", PLANT_SEED, phase="flowering", date="2026-09-10")
    assert _state(hass, "sensor", PLANT_SEED, "days_in_phase").state == "5"
    assert len(events) == 2


async def test_set_phase_invalid_date(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    with pytest.raises(ServiceValidationError):
        await _call(hass, "set_phase", PLANT_SEED, phase="vegetative", date="2026-08-01")


async def test_select_phase_option(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": _eid(hass, "select", PLANT_SEED, "phase"), "option": "vegetative"},
        blocking=True,
    )
    assert _state(hass, "select", PLANT_SEED, "phase").state == "vegetative"


async def test_move_location(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    events = async_capture_events(hass, "grow_tracker_location_changed")

    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": _eid(hass, "select", PLANT_SEED, "location"), "option": "Anzucht"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert _state(hass, "select", PLANT_SEED, "location").state == "Anzucht"
    assert _state(hass, "sensor", LOC_FLOWER, "plant_count").state == "0"
    assert _state(hass, "sensor", LOC_PROP, "plant_count").state == "1"

    # Dienst per Name, Groß-/Kleinschreibung egal
    await _call(hass, "set_location", PLANT_SEED, location="BLÜTE groß")
    assert _state(hass, "select", PLANT_SEED, "location").state == "Blüte groß"
    assert [(e.data["from_location"], e.data["to_location"]) for e in events] == [
        ("Blüte groß", "Anzucht"),
        ("Anzucht", "Blüte groß"),
    ]

    with pytest.raises(ServiceValidationError):
        await _call(hass, "set_location", PLANT_SEED, location="Gibt es nicht")


async def test_area_sync(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    area = ar.async_get(hass).async_create("Growraum")
    # Standort "Anzucht" bekommt einen Bereich
    sub = mock_entry.subentries[LOC_PROP]
    mock_entry.add_to_hass(hass)
    hass.config_entries.async_update_subentry(
        mock_entry, sub, data={**sub.data, "area_id": area.id}
    )
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    dev_reg = dr.async_get(hass)
    loc_device = dev_reg.async_get_device(identifiers={(DOMAIN, LOC_PROP)})
    assert loc_device.area_id == area.id

    plant_device = dev_reg.async_get_device(identifiers={(DOMAIN, PLANT_SEED)})
    assert plant_device.area_id != area.id

    await _call(hass, "set_location", PLANT_SEED, location="Anzucht")
    plant_device = dev_reg.async_get_device(identifiers={(DOMAIN, PLANT_SEED)})
    assert plant_device.area_id == area.id


async def test_add_note(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    events = async_capture_events(hass, "grow_tracker_note_added")
    await _call(hass, "add_note", PLANT_SEED, note="Erste Blätter")

    note = _state(hass, "sensor", PLANT_SEED, "last_note")
    assert note.state == "Erste Blätter"
    assert note.attributes["count"] == 1
    assert note.attributes["notes"][0]["location"] == "Blüte groß"
    assert events[0].data["day"] == 14


async def test_take_cuttings_log_only(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    await _call(hass, "take_cuttings", PLANT_MOTHER, count=4)
    sensor = _state(hass, "sensor", PLANT_MOTHER, "cuttings_taken")
    assert sensor.state == "4"
    assert sensor.attributes["log"] == [{"date": "2026-09-15", "count": 4}]
    assert len(setup_entry.runtime_data.plants) == 2


async def test_take_cuttings_create_plants(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    await _call(hass, "take_cuttings", PLANT_MOTHER, count=3, create_plants=True)
    await hass.async_block_till_done()

    hub = setup_entry.runtime_data  # nach dem Reload neu
    cuttings = sorted(
        (p for p in hub.plants.values() if p.mother_id == PLANT_MOTHER), key=lambda p: p.name
    )
    assert [p.name for p in cuttings] == ["Mutter Gelato #1", "Mutter Gelato #2", "Mutter Gelato #3"]
    for plant in cuttings:
        assert plant.phase == "rooting"
        assert plant.strain == "Gelato"
        assert plant.location_id == LOC_PROP  # erster Anzucht-Standort
        assert _state(hass, "select", plant.subentry_id, "phase").state == "rooting"

    sensor = _state(hass, "sensor", PLANT_MOTHER, "cuttings_taken")
    assert sensor.state == "3"
    assert len(sensor.attributes["tracked_cuttings"]) == 3
    assert _state(hass, "sensor", LOC_PROP, "plant_count").state == "3"


async def test_take_cuttings_requires_mother(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError):
        await _call(hass, "take_cuttings", PLANT_SEED, count=1)


async def test_persistence(
    hass: HomeAssistant, setup_entry: MockConfigEntry, frozen_today: FrozenDateTimeFactory
) -> None:
    await _call(hass, "set_phase", PLANT_SEED, phase="vegetative")
    await _call(hass, "add_note", PLANT_SEED, note="Gedüngt")

    assert await hass.config_entries.async_reload(setup_entry.entry_id)
    await hass.async_block_till_done()

    assert _state(hass, "select", PLANT_SEED, "phase").state == "vegetative"
    assert _state(hass, "sensor", PLANT_SEED, "last_note").state == "Gedüngt"

    # Tageszähler springt um Mitternacht weiter
    frozen_today.move_to("2026-09-16 00:00:10+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _state(hass, "sensor", PLANT_SEED, "days_total").state == "15"


async def test_remove_plant(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    entity_id = _eid(hass, "select", PLANT_SEED, "phase")
    hass.config_entries.async_remove_subentry(setup_entry, PLANT_SEED)
    await hass.async_block_till_done()

    assert PLANT_SEED not in setup_entry.runtime_data.plants
    assert er.async_get(hass).async_get(entity_id) is None
    assert dr.async_get(hass).async_get_device(identifiers={(DOMAIN, PLANT_SEED)}) is None
    assert _state(hass, "sensor", LOC_FLOWER, "plant_count").state == "0"


async def test_mother_location_unchanged(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    """Gleicher Standort ohne Datum ist ein No-Op."""
    plant = setup_entry.runtime_data.plants[PLANT_MOTHER]
    await plant.async_set_location(LOC_MOTHER)
    assert len(plant.location_history) == 1
