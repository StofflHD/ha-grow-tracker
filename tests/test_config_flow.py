"""Tests für Setup-Assistent und Subentry-Flows."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import LOC_FLOWER, LOC_MOTHER, PLANT_MOTHER


async def test_setup_wizard(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"locations": ["Mutterschrank", " Blüte groß ", ""]}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "location"
    assert result["description_placeholders"] == {
        "name": "Mutterschrank",
        "current": "1",
        "total": "2",
    }
    # Art wird aus dem Namen vorgeschlagen
    defaults = {str(k): k.default() for k in result["data_schema"].schema if hasattr(k, "default") and callable(k.default)}
    assert defaults["location_type"] == "mother"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"location_type": "mother"}
    )
    assert result["step_id"] == "location"
    assert result["description_placeholders"]["name"] == "Blüte groß"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"location_type": "flowering"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    locations = sorted(
        (sub.title, sub.data["location_type"])
        for sub in entry.subentries.values()
        if sub.subentry_type == "location"
    )
    assert locations == [("Blüte groß", "flowering"), ("Mutterschrank", "mother")]


async def test_setup_wizard_errors(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"locations": [" "]})
    assert result["errors"] == {"base": "no_locations"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"locations": ["Zelt", "zelt"]}
    )
    assert result["errors"] == {"base": "duplicate_name"}


async def test_single_instance(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_add_location(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "location"), context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "mutterschrank", "location_type": "other"}
    )
    assert result["errors"] == {"base": "duplicate_name"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Blüte mini", "location_type": "flowering"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    hub = setup_entry.runtime_data
    assert "Blüte mini" in [loc.name for loc in hub.locations.values()]


async def test_reconfigure_location(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "location"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": LOC_FLOWER},
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Anzucht", "location_type": "flowering"}
    )
    assert result["errors"] == {"base": "duplicate_name"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Blütezelt XL", "location_type": "flowering"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    assert setup_entry.runtime_data.locations[LOC_FLOWER].name == "Blütezelt XL"


async def test_add_plant_as_cutting(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"name": "Gelato Klon", "mother": PLANT_MOTHER, "location": LOC_MOTHER, "flower_weeks": 8},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    hub = setup_entry.runtime_data
    plant = next(p for p in hub.plants.values() if p.name == "Gelato Klon")
    assert plant.phase == "rooting"
    assert plant.strain == "Gelato"
    assert plant.mother_name == "Mutter Gelato"
    assert plant.flower_weeks == 8
    assert plant.location_name == "Mutterschrank"


async def test_add_plant_without_locations(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, version=2, title="Grow Tracker", data={})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_locations"


async def test_reconfigure_plant(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": PLANT_MOTHER},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Mama Gelato", "flower_weeks": 10}
    )
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    plant = setup_entry.runtime_data.plants[PLANT_MOTHER]
    assert plant.name == "Mama Gelato"
    assert plant.strain is None  # Feld geleert
    assert plant.flower_weeks == 10
    assert plant.phase == "mother"  # Historie bleibt erhalten
