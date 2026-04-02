# OWCS Korea 2026 Stage 1 Map Pool

## Source Rule

This map pool record is based on the Overwatch Liquipedia map pool information provided during review.

## Map Pool By Mode

### Control

- Busan
- Lijiang Tower
- Oasis

### Hybrid

- Blizzard World
- Midtown
- Numbani

### Flashpoint

- Aatlis
- Suravasa

### Push

- Esperanca
- Runasapi

### Escort

- Havana
- Rialto
- Watchpoint: Gibraltar

## Structured Record

```json
[
  { "map_name": "Busan", "map_mode": "Control" },
  { "map_name": "Lijiang Tower", "map_mode": "Control" },
  { "map_name": "Oasis", "map_mode": "Control" },
  { "map_name": "Blizzard World", "map_mode": "Hybrid" },
  { "map_name": "Midtown", "map_mode": "Hybrid" },
  { "map_name": "Numbani", "map_mode": "Hybrid" },
  { "map_name": "Aatlis", "map_mode": "Flashpoint" },
  { "map_name": "Suravasa", "map_mode": "Flashpoint" },
  { "map_name": "Esperanca", "map_mode": "Push" },
  { "map_name": "Runasapi", "map_mode": "Push" },
  { "map_name": "Havana", "map_mode": "Escort" },
  { "map_name": "Rialto", "map_mode": "Escort" },
  { "map_name": "Watchpoint: Gibraltar", "map_mode": "Escort" }
]
```

## Notes

- Map names are recorded in the exact form we plan to use in OWCStats.
- The mode mapping should be treated as baseline reference data for later match result and player stat processing.
