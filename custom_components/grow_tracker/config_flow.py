"""Setup-Assistent sowie Subentry-Flows für Standorte und Pflanzen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigEntryState,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryData,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    AreaSelector,
    DateSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    CONF_AREA,
    CONF_FLOWER_WEEKS,
    CONF_LOCATION,
    CONF_LOCATION_TYPE,
    CONF_LOCATIONS,
    CONF_MOTHER,
    CONF_MOTHER_NAME,
    CONF_PHASE,
    CONF_PHENOTYPE,
    CONF_START_DATE,
    CONF_STRAIN,
    DEFAULT_FLOWER_WEEKS,
    DOMAIN,
    LOCATION_TYPE_DRYING,
    LOCATION_TYPE_FLOWERING,
    LOCATION_TYPE_MOTHER,
    LOCATION_TYPE_OTHER,
    LOCATION_TYPE_PROPAGATION,
    LOCATION_TYPE_VEGETATIVE,
    LOCATION_TYPES,
    PHASE_MOTHER,
    PHASES,
    SUBENTRY_LOCATION,
    SUBENTRY_PLANT,
)
from .hub import async_propagate_to_cuttings

FLOWER_WEEKS_SELECTOR = NumberSelector(
    NumberSelectorConfig(min=4, max=16, step=1, mode=NumberSelectorMode.BOX)
)

# Stichwörter, um die Art eines Standorts aus dem Namen vorzuschlagen
_TYPE_KEYWORDS = (
    (LOCATION_TYPE_MOTHER, ("mutter", "mother")),
    (LOCATION_TYPE_PROPAGATION, ("steckling", "anzucht", "propag", "clone", "klon")),
    (LOCATION_TYPE_FLOWERING, ("blüte", "bluete", "flower", "bloom")),
    (LOCATION_TYPE_DRYING, ("trock", "dry")),
    (LOCATION_TYPE_VEGETATIVE, ("wachs", "veg")),
)


def _guess_location_type(name: str) -> str:
    lowered = name.casefold()
    for location_type, words in _TYPE_KEYWORDS:
        if any(word in lowered for word in words):
            return location_type
    return LOCATION_TYPE_OTHER


def _location_details_schema(default_type: str) -> dict[Any, Any]:
    return {
        vol.Required(CONF_LOCATION_TYPE, default=default_type): SelectSelector(
            SelectSelectorConfig(
                options=LOCATION_TYPES,
                translation_key="location_type",
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_AREA): AreaSelector(),
    }


def _location_names(entry: ConfigEntry, exclude: str | None = None) -> set[str]:
    return {
        sub.title.casefold()
        for sub in entry.subentries.values()
        if sub.subentry_type == SUBENTRY_LOCATION and sub.subentry_id != exclude
    }


class GrowTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Erst-Einrichtung: Standorte nacheinander anlegen."""

    VERSION = 2

    def __init__(self) -> None:
        self._names: list[str] = []
        self._locations: list[ConfigSubentryData] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            names = [n.strip() for n in user_input[CONF_LOCATIONS] if n.strip()]
            if not names:
                errors["base"] = "no_locations"
            elif len({n.casefold() for n in names}) != len(names):
                errors["base"] = "duplicate_name"
            else:
                self._names = names
                return await self.async_step_location()

        schema = vol.Schema(
            {
                vol.Required(CONF_LOCATIONS): TextSelector(
                    TextSelectorConfig(multiple=True)
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Art und Bereich für jeden Standort abfragen."""
        if user_input is not None:
            self._locations.append(
                ConfigSubentryData(
                    data=user_input,
                    subentry_type=SUBENTRY_LOCATION,
                    title=self._names[len(self._locations)],
                    unique_id=None,
                )
            )

        if len(self._locations) == len(self._names):
            return self.async_create_entry(
                title="Grow Tracker", data={}, subentries=self._locations
            )

        name = self._names[len(self._locations)]
        return self.async_show_form(
            step_id="location",
            data_schema=vol.Schema(_location_details_schema(_guess_location_type(name))),
            description_placeholders={
                "name": name,
                "current": str(len(self._locations) + 1),
                "total": str(len(self._names)),
            },
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {
            SUBENTRY_LOCATION: LocationSubentryFlow,
            SUBENTRY_PLANT: PlantSubentryFlow,
        }


class LocationSubentryFlow(ConfigSubentryFlow):
    """Standort hinzufügen / bearbeiten."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input.pop(CONF_NAME).strip()
            if name.casefold() in _location_names(self._get_entry()):
                errors["base"] = "duplicate_name"
            else:
                return self.async_create_entry(title=name, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): TextSelector(),
                **_location_details_schema(LOCATION_TYPE_OTHER),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.pop(CONF_NAME).strip()
            if name.casefold() in _location_names(entry, exclude=subentry.subentry_id):
                errors["base"] = "duplicate_name"
            else:
                return self.async_update_and_abort(
                    entry, subentry, title=name, data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): TextSelector(),
                **_location_details_schema(LOCATION_TYPE_OTHER),
            }
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                schema, {CONF_NAME: subentry.title, **subentry.data}
            ),
            errors=errors,
        )


class PlantSubentryFlow(ConfigSubentryFlow):
    """Pflanze hinzufügen / bearbeiten."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        entry = self._get_entry()
        if entry.state is not ConfigEntryState.LOADED:
            return self.async_abort(reason="not_loaded")
        hub = entry.runtime_data
        if not hub.locations:
            return self.async_abort(reason="no_locations")

        mothers = {
            pid: plant for pid, plant in hub.plants.items() if plant.phase == PHASE_MOTHER
        }

        if user_input is not None:
            data = dict(user_input)
            name = data.pop(CONF_NAME).strip()
            data[CONF_FLOWER_WEEKS] = int(data[CONF_FLOWER_WEEKS])
            if (mother := mothers.get(data.get(CONF_MOTHER, ""))) is not None:
                data[CONF_MOTHER_NAME] = mother.name
                # Breeder/Cutter und Phänotyp von der Mutter übernehmen, falls leer
                if not data.get(CONF_STRAIN) and mother.strain:
                    data[CONF_STRAIN] = mother.strain
                if not data.get(CONF_PHENOTYPE) and mother.phenotype:
                    data[CONF_PHENOTYPE] = mother.phenotype
            return self.async_create_entry(title=name, data=data)

        fields: dict[Any, Any] = {
            vol.Required(CONF_NAME): TextSelector(),
            vol.Optional(CONF_STRAIN): TextSelector(),
            vol.Optional(CONF_PHENOTYPE): TextSelector(),
        }
        if mothers:
            fields[vol.Optional(CONF_MOTHER)] = SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=pid, label=plant.name)
                        for pid, plant in mothers.items()
                    ],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            )
        fields.update(
            {
                vol.Optional(CONF_PHASE): SelectSelector(
                    SelectSelectorConfig(
                        options=PHASES,
                        translation_key="phase",
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_LOCATION, default=next(iter(hub.locations))
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=lid, label=loc.name)
                            for lid, loc in hub.locations.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_START_DATE): DateSelector(),
                vol.Required(
                    CONF_FLOWER_WEEKS, default=DEFAULT_FLOWER_WEEKS
                ): FLOWER_WEEKS_SELECTOR,
            }
        )
        return self.async_show_form(step_id="user", data_schema=vol.Schema(fields))

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Nur Stammdaten – Phasen und Standorte laufen über die Entities."""
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            data = dict(user_input)
            name = data.pop(CONF_NAME).strip()
            data[CONF_FLOWER_WEEKS] = int(data[CONF_FLOWER_WEEKS])
            new_data = {**subentry.data, **data}
            for optional in (CONF_STRAIN, CONF_PHENOTYPE):
                if not data.get(optional):
                    new_data.pop(optional, None)

            # Während Mutter und Stecklinge aktualisiert werden, nur einmal am Ende neu laden
            hub = entry.runtime_data if entry.state is ConfigEntryState.LOADED else None
            if hub is not None:
                hub.reload_pending = True
            updated = async_propagate_to_cuttings(
                self.hass,
                entry,
                subentry.subentry_id,
                subentry.title,
                dict(subentry.data),
                name,
                new_data,
            )
            result = self.async_update_and_abort(entry, subentry, title=name, data=new_data)
            if hub is not None:
                if updated:
                    self.hass.config_entries.async_schedule_reload(entry.entry_id)
                else:
                    hub.reload_pending = False
            return result

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): TextSelector(),
                vol.Optional(CONF_STRAIN): TextSelector(),
                vol.Optional(CONF_PHENOTYPE): TextSelector(),
                vol.Required(CONF_FLOWER_WEEKS): FLOWER_WEEKS_SELECTOR,
            }
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                schema,
                {
                    CONF_NAME: subentry.title,
                    CONF_STRAIN: subentry.data.get(CONF_STRAIN),
                    CONF_PHENOTYPE: subentry.data.get(CONF_PHENOTYPE),
                    CONF_FLOWER_WEEKS: subentry.data.get(
                        CONF_FLOWER_WEEKS, DEFAULT_FLOWER_WEEKS
                    ),
                },
            ),
        )
