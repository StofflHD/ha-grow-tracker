"""Tests: mehrere gleiche Pflanzen (z. B. Samen) auf einmal anlegen."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import SOURCE_USER, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import LOC_PROP


async def _add_plants(hass: HomeAssistant, entry: MockConfigEntry, **user_input: Any):
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"location": LOC_PROP, "flower_weeks": 9, **user_input},
    )
    await hass.async_block_till_done()
    return result


def _names(entry: MockConfigEntry, prefix: str) -> list[str]:
    return sorted(
        (p.name for p in entry.runtime_data.plants.values() if p.name.startswith(prefix)),
        key=lambda n: (len(n), n),
    )


async def test_create_several_seeds(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    with patch.object(
        hass.config_entries, "async_reload", wraps=hass.config_entries.async_reload
    ) as reload:
        result = await _add_plants(
            hass,
            setup_entry,
            name="Zkittlez",
            count=3,
            strain="Dutch Passion",
            phase="germination",
            start_date="2026-09-10",
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "plants_created"
    assert result["description_placeholders"] == {
        "count": "3",
        "first": "Zkittlez #1",
        "last": "Zkittlez #3",
    }
    assert reload.call_count == 1

    assert _names(setup_entry, "Zkittlez") == ["Zkittlez #1", "Zkittlez #2", "Zkittlez #3"]
    for plant in setup_entry.runtime_data.plants.values():
        if plant.name.startswith("Zkittlez"):
            assert plant.strain == "Dutch Passion"
            assert plant.phase == "germination"
            assert plant.grow_start.isoformat() == "2026-09-10"
            assert plant.location_id == LOC_PROP
            assert plant.origin == "seed"
    assert setup_entry.runtime_data.reload_pending is False  # neuer Hub nach dem Reload


async def test_numbering_continues(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    hass.config_entries.async_add_subentry(
        setup_entry,
        ConfigSubentry(
            data=MappingProxyType({"location": LOC_PROP, "flower_weeks": 9}),
            subentry_type="plant",
            title="Zkittlez #2",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()

    result = await _add_plants(hass, setup_entry, name="Zkittlez", count=2)
    assert result["description_placeholders"]["first"] == "Zkittlez #3"
    assert _names(setup_entry, "Zkittlez") == ["Zkittlez #2", "Zkittlez #3", "Zkittlez #4"]


async def test_single_plant_unchanged(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await _add_plants(hass, setup_entry, name="Zkittlez", count=1)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert _names(setup_entry, "Zkittlez") == ["Zkittlez"]
    # Die Anzahl wird nicht mitgespeichert
    plant = next(p for p in setup_entry.runtime_data.plants.values() if p.name == "Zkittlez")
    assert "count" not in plant.subentry.data
