# OWCS VOD Analysis Plan

## Goal

Build a first-pass OWCS VOD analysis pipeline that automatically downloads match footage, prepares map clips, extracts player-plus-hero timeline events, and stores reviewable event data for later stat comparisons.

This phase prioritizes accuracy over speed.

## Phase 1 Scope

Phase 1 will focus on these outcomes:

- download a VOD from a source link
- save a local mp4 for analysis
- prepare match or map clips for processing
- detect player-plus-hero state from the top HUD
- detect kill feed events from the top-right feed
- track ultimate-ready timing and ultimate-use timing
- detect hero swaps
- determine first kill and first death per combat event window
- save outputs as raw JSON plus SQLite records
- present a reviewable table for manual verification

Phase 1 will not yet finalize teamfight duration rules beyond first-kill event windows.

## Input Workflow

Primary input mode:

- VOD link

Planned ingest flow:

1. Download the source VOD to local storage.
2. Prepare a local mp4 for analysis.
3. Cut analysis clips by match or map when timestamps are available.
4. If start and end timestamps are unclear, generate candidate boundaries and allow manual timestamp input.

Manual support rule:

- If needed, the user can provide match start and end timestamps.

## Core Tracking Unit

All event tracking is based on:

- player + hero

This pairing is the primary label for ultimate tracking and hero-state changes.

## Priority Metrics

Priority order for Phase 1:

1. Time to ultimate-ready state
2. First death and first kill involvement
3. Fight duration

Fight duration remains a later rule layer and depends on stable raw event extraction first.

## Event Definitions

### Ultimate Ready

Record an ultimate-ready event when:

- the HUD ultimate icon appears fully charged
- the fully charged state remains visible for at least 2 consecutive seconds

Phase 1 timing precision target:

- second-level accuracy

### Ultimate Charge Start Points

Start a new ultimate charge window when any of the following occur:

- the map begins for that player-plus-hero
- the player uses their previous ultimate
- the player swaps to a new hero and that hero remains active long enough to confirm the swap

### Ultimate Use

Record an ultimate-use event when:

- the HUD changes from a charged icon state back to a numeric charge display

### Hero Swap

Record a hero swap only when:

- the top HUD hero icon changes
- the new hero remains visible for at least 10 seconds

### Kill Feed Event

Phase 1 kill feed storage fields:

- killer_player
- killer_hero
- victim_player
- victim_hero

These fields are sufficient for first-kill and first-death calculations in the first version.

### First Kill / First Death Qualification

Only consider a kill as the start of a tracked combat event when:

- all 10 players are alive
- that full-alive state lasts for at least 15 consecutive seconds
- then the next qualifying kill occurs

For each such event window:

- first kill is the first qualifying kill feed event
- first death is the victim from that same first qualifying kill feed event

This rule is applied at the map level.

## Special Hero Rules

### Echo

Exclude temporary ultimate charge gained while transformed into another hero after Echo uses Duplicate.

### D.Va

Do not count the post-demech Call Mech charge cycle as a normal ultimate charge timing window.

Store demech-related events under one unified internal event name.

## Review Workflow

The first review experience will be table-based.

Review goals:

- inspect extracted ultimate-ready events
- inspect ultimate-use events
- inspect hero swaps
- inspect first-kill and first-death rows
- correct uncertain outputs manually when needed

## Storage Plan

Store outputs in two layers:

1. Raw JSON
2. SQLite

Suggested responsibilities:

- JSON stores raw frame or detection outputs for traceability
- SQLite stores normalized timeline events for querying and metric generation

## Proposed Implementation Order

1. Build or extend the ingest pipeline for VOD download and local clip preparation.
2. Define the normalized event schema for JSON and SQLite.
3. Implement top-HUD parsing for player, hero, and ultimate state tracking.
4. Implement kill feed parsing for killer and victim extraction.
5. Add rule logic for ultimate-ready timing, ultimate-use timing, and hero swap confirmation.
6. Add first-kill and first-death logic using the 15-second all-alive gate.
7. Generate a review table for each analyzed map.
8. Add confidence handling and manual correction support.

## Success Criteria For Phase 1

Phase 1 is successful when the system can:

- take a VOD link and produce a local analysis-ready file
- analyze one map end-to-end
- emit reviewable rows for ultimate-ready, ultimate-use, hero-swap, and first-kill events
- preserve enough raw evidence to manually verify questionable cases
- support later derived metrics without changing the base event structure

## Immediate Next Step

Implement the ingestion and event schema foundation first, then build the HUD and kill-feed extractors on top of that shared structure.
