# Automations and Dashboards

## Events

| Event | Data |
|---|---|
| `grow_tracker_phase_changed` | `plant`, `plant_id`, `from_phase`, `to_phase`, `date` |
| `grow_tracker_location_changed` | `plant`, `plant_id`, `from_location`, `to_location`, `date` |
| `grow_tracker_cuttings_taken` | `plant`, `plant_id`, `count`, `date`, `created_plants` |
| `grow_tracker_note_added` | `plant`, `plant_id`, `id`, `date`, `location`, `phase`, `day`, `text` |

Corrections of the history in the panel do **not** fire events.

## Automation examples

### Reminder: switch light to 12/12 when flowering starts

```yaml
alias: Grow – flowering started
triggers:
  - trigger: event
    event_type: grow_tracker_phase_changed
    event_data:
      to_phase: flowering
actions:
  - action: notify.notify
    data:
      message: "{{ trigger.event.data.plant }} started flowering – switch the light to 12/12!"
```

### Harvest is due

```yaml
alias: Grow – harvest due
triggers:
  - trigger: time
    at: "09:00:00"
conditions:
  - condition: template
    value_template: "{{ state_attr('sensor.gelato_41_expected_harvest', 'days_remaining') | int(99) <= 0 }}"
actions:
  - action: notify.notify
    data:
      message: "Gelato #41 is ready for harvest."
```

### Note when the light schedule changes

```yaml
alias: Grow – log light change
triggers:
  - trigger: state
    entity_id: input_select.flower_tent_light
actions:
  - action: grow_tracker.add_note
    target:
      entity_id: select.gelato_41_phase
    data:
      note: "Light changed to {{ trigger.to_state.state }}"
```

### Cuttings rooted after 14 days

```yaml
alias: Grow – rooting check
triggers:
  - trigger: time
    at: "08:00:00"
actions:
  - repeat:
      for_each: >
        {{ integration_entities('grow_tracker')
           | select('match', 'select\..*_phase$')
           | select('is_state', 'rooting') | list }}
      sequence:
        - condition: template
          value_template: >
            {{ (now().date() - strptime(state_attr(repeat.item, 'phase_start'), '%Y-%m-%d').date()).days >= 14 }}
        - action: notify.notify
          data:
            message: "{{ state_attr(repeat.item, 'friendly_name') }}: rooting for 14 days – time to check!"
```

## Dashboard examples

The [Sidebar Panel](Sidebar-Panel.md) is the easiest overview. For your own dashboards:

### Entities card for one plant

```yaml
type: entities
title: Gelato #41
entities:
  - select.gelato_41_phase
  - select.gelato_41_location
  - sensor.gelato_41_days_total
  - sensor.gelato_41_week_in_phase
  - sensor.gelato_41_expected_harvest
  - sensor.gelato_41_last_note
```

### Plants per location

```yaml
type: glance
title: Locations
entities:
  - sensor.mother_cabinet_plants
  - sensor.flower_large_plants
  - sensor.flower_small_plants
```

### Area dashboard

Assign an **area** to each location (see [Setup](Setup.md)). The area page then shows the plants of that tent
together with its climate sensors, light and fans.

---

[← Documentation overview](README.md)
