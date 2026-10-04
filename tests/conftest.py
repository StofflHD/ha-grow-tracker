"""Gemeinsame Fixtures."""

from __future__ import annotations

from collections.abc import Generator
import sys

from freezegun.api import FrozenDateTimeFactory
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import pytest_socket

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.core import HomeAssistant

START = "2026-09-01"

LOC_MOTHER = "loc_mother"
LOC_FLOWER = "loc_flower"
LOC_PROP = "loc_prop"
PLANT_MOTHER = "plant_mother"
PLANT_SEED = "plant_seed"


if sys.platform == "win32":
    # Die Windows-Event-Loop braucht ein lokales TCP-Socket-Paar (Linux nutzt Unix-Sockets),
    # das pytest-socket sonst blockiert. Unter Linux/CI bleibt der Schutz aktiv.
    pytest_socket.disable_socket = lambda *args, **kwargs: None


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    yield


@pytest.fixture(autouse=True)
async def frozen_today(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> FrozenDateTimeFactory:
    """Fester „Heute“-Wert: 15.09.2026, 12:00 Uhr in Berlin."""
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to("2026-09-15 12:00:00+02:00")
    return freezer


def _location(subentry_id: str, title: str, location_type: str, **extra) -> dict:
    return {
        "data": {"location_type": location_type, **extra},
        "subentry_id": subentry_id,
        "subentry_type": "location",
        "title": title,
        "unique_id": None,
    }


def _plant(subentry_id: str, title: str, **data) -> dict:
    return {
        "data": {"flower_weeks": 9, **data},
        "subentry_id": subentry_id,
        "subentry_type": "plant",
        "title": title,
        "unique_id": None,
    }


@pytest.fixture
def mock_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        version=2,
        title="Grow Tracker",
        data={},
        subentries_data=[
            _location(LOC_MOTHER, "Mutterschrank", "mother"),
            _location(LOC_FLOWER, "Blüte groß", "flowering"),
            _location(LOC_PROP, "Anzucht", "propagation"),
            _plant(
                PLANT_MOTHER,
                "Mutter Gelato",
                strain="Gelato",
                phenotype="Pheno #3",
                phase="mother",
                location=LOC_MOTHER,
                start_date=START,
            ),
            _plant(
                PLANT_SEED,
                "Northern Lights",
                location=LOC_FLOWER,
                start_date=START,
            ),
        ],
    )


@pytest.fixture
async def setup_entry(hass: HomeAssistant, mock_entry: MockConfigEntry) -> MockConfigEntry:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()
    return mock_entry
