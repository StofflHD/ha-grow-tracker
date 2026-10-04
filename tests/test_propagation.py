"""Tests: Änderungen an einer Mutter werden an ihre Stecklinge weitergegeben."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.config_entries import SOURCE_RECONFIGURE, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import LOC_PROP, PLANT_MOTHER


async def _take_cuttings(hass: HomeAssistant, count: int) -> None:
    entity_id = er.async_get(hass).async_get_entity_id("select", DOMAIN, f"{PLANT_MOTHER}_phase")
    await hass.services.async_call(
        DOMAIN,
        "take_cuttings",
        {"entity_id": entity_id, "count": count, "create_plants": True},
        blocking=True,
    )
    await hass.async_block_till_done()


def _add_plant(hass: HomeAssistant, entry: MockConfigEntry, plant_id: str, title: str, **data: Any) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data=MappingProxyType({"location": LOC_PROP, "flower_weeks": 9, **data}),
            subentry_type="plant",
            title=title,
            unique_id=None,
            subentry_id=plant_id,
        ),
    )


async def _reconfigure(hass: HomeAssistant, entry: MockConfigEntry, plant_id: str, **user_input: Any) -> None:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": plant_id},
    )
    result = await hass.config_entries.subentries.async_configure(result["flow_id"], user_input)
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()


async def test_mother_changes_reach_cuttings(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    await _take_cuttings(hass, 2)

    with patch.object(
        hass.config_entries, "async_reload", wraps=hass.config_entries.async_reload
    ) as reload:
        await _reconfigure(
            hass,
            setup_entry,
            PLANT_MOTHER,
            name="Gelato #41",
            strain="Seed Junky",
            phenotype="Pheno #5",
            flower_weeks=10,
        )
    assert reload.call_count == 1  # Mutter + 2 Stecklinge, nur ein Reload

    hub = setup_entry.runtime_data
    cuttings = sorted((p for p in hub.plants.values() if p.mother_id), key=lambda p: p.name)
    assert [p.name for p in cuttings] == ["Gelato #41 #1", "Gelato #41 #2"]
    for plant in cuttings:
        assert plant.strain == "Seed Junky"
        assert plant.phenotype == "Pheno #5"
        assert plant.flower_weeks == 10
        assert plant.mother_name == "Gelato #41"
        assert plant.phase == "rooting"  # Historie bleibt erhalten
    assert hub.plants[PLANT_MOTHER].name == "Gelato #41"


async def test_individual_values_are_kept(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    # Steckling mit eigenem Namen und eigenem Breeder/Cutter, aber geerbtem Phänotyp
    _add_plant(
        hass,
        setup_entry,
        "own",
        "Mein Klon",
        mother=PLANT_MOTHER,
        mother_name="Mutter Gelato",
        strain="Eigener Cutter",
        phenotype="Pheno #3",
    )
    await hass.async_block_till_done()

    await _reconfigure(
        hass, setup_entry, PLANT_MOTHER, name="Gelato", strain="Neu", phenotype="Pheno #9", flower_weeks=9
    )

    clone = setup_entry.runtime_data.plants["own"]
    assert clone.name == "Mein Klon"  # eigener Name bleibt
    assert clone.strain == "Eigener Cutter"  # individuell geändert → bleibt
    assert clone.phenotype == "Pheno #9"  # geerbt → übernommen
    assert clone.mother_name == "Gelato"


async def test_cleared_field_is_cleared_on_cuttings(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    await _take_cuttings(hass, 1)
    await _reconfigure(hass, setup_entry, PLANT_MOTHER, name="Mutter Gelato", strain="Gelato", flower_weeks=9)

    cutting = next(p for p in setup_entry.runtime_data.plants.values() if p.mother_id)
    assert cutting.phenotype is None
    assert cutting.strain == "Gelato"


async def test_grandchildren(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    """Stecklinge von Stecklingen werden ebenfalls aktualisiert."""
    _add_plant(
        hass, setup_entry, "child", "Mutter Gelato #1",
        mother=PLANT_MOTHER, mother_name="Mutter Gelato", strain="Gelato", phenotype="Pheno #3",
    )
    _add_plant(
        hass, setup_entry, "grandchild", "Mutter Gelato #1 #1",
        mother="child", mother_name="Mutter Gelato #1", strain="Gelato", phenotype="Pheno #3",
    )
    await hass.async_block_till_done()

    await _reconfigure(
        hass, setup_entry, PLANT_MOTHER, name="Gelato", strain="Seed Junky", phenotype="Pheno #3", flower_weeks=9
    )

    plants = setup_entry.runtime_data.plants
    assert plants["child"].name == "Gelato #1"
    assert plants["grandchild"].name == "Gelato #1 #1"
    assert plants["grandchild"].strain == "Seed Junky"
    assert plants["grandchild"].mother_name == "Gelato #1"


async def test_plant_without_cuttings_reloads_normally(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    await _reconfigure(
        hass, setup_entry, PLANT_MOTHER, name="Mama", strain="Gelato", phenotype="Pheno #3", flower_weeks=9
    )
    hub = setup_entry.runtime_data
    assert hub.plants[PLANT_MOTHER].name == "Mama"
    assert hub.reload_pending is False
