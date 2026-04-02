# OWCStats

## Goal

OWCStats is an AI-assisted analysis system for the Overwatch Champions Series (OWCS).

The core goal is to organize player-by-player match performance data from match videos without relying on separate third-party analysis programs.

## What We Want To Build

The system should help turn match footage into structured player statistics.

Examples of target outputs:

- player eliminations
- deaths
- assists
- final blows
- hero usage
- ultimate usage timing
- fight participation
- map-by-map performance summaries
- match-by-match player reports

## Core Product Idea

Instead of manually tagging matches, OWCStats should use AI to inspect game footage and extract useful events.

High-level pipeline:

1. Ingest a match video
2. Split the video into frames or short clips
3. Detect game UI elements and key moments from frames
4. Identify players, heroes, teams, score state, and combat events
5. Convert detected events into structured records
6. Aggregate records into player statistics
7. Review and correct uncertain outputs through a human-friendly interface

## Important Reality Check

A fully automatic system from raw video to perfect statistics is difficult.

The practical version should be built in stages:

1. Semi-automatic analysis first
2. Human review for uncertain events
3. Gradual improvement of AI detection over time

This approach is more realistic and will produce useful results faster.

## Suggested V1 Scope

Version 1 should focus on a narrow but useful workflow:

- upload or point to a match video
- extract frames at intervals
- detect scoreboard / HUD information
- identify visible player names and hero picks
- detect kill feed events when visible
- save extracted events to a local database
- show a per-player summary dashboard

## Proposed System Architecture

### 1. Video Processing Layer

Responsibilities:

- load local video files
- sample frames
- cut clips around key timestamps

Possible tools:

- Python
- FFmpeg
- OpenCV

### 2. AI Extraction Layer

Responsibilities:

- analyze frames
- interpret HUD elements
- infer structured game events

Possible methods:

- vision-capable LLM calls for frame interpretation
- OCR for player names and scores
- custom detectors later if needed

### 3. Data Layer

Responsibilities:

- store matches
- store players
- store maps
- store detected events
- store aggregated stats

Possible starting choice:

- SQLite for local development

### 4. Review Layer

Responsibilities:

- show extracted events
- highlight low-confidence detections
- allow manual correction

### 5. Dashboard Layer

Responsibilities:

- player profile pages
- map summaries
- match summaries
- searchable stats tables

## Recommended Tech Stack For First Build

To move quickly, start with:

- Python backend
- SQLite database
- FFmpeg for video frame extraction
- OpenCV for basic frame handling
- OCR and vision model integration for event extraction
- simple web UI later with FastAPI + lightweight frontend

## Initial Data Model

Key entities:

- Region
- Tournament
- Match
- Map
- Team
- Player
- Hero
- VideoSource
- DetectedEvent
- PlayerMatchStat

## Biggest Challenges

- broadcast overlays changing by region or event
- observer camera not always showing all players
- kill feed visibility and timing
- OCR noise on player names
- hero swaps and spectator delays
- partial information when HUD is hidden

## Best Development Strategy

Build this in phases.

### Phase 1

Create the local project structure and ingest pipeline.

### Phase 2

Extract frames and detect visible HUD data from still images.

### Phase 3

Turn detections into structured events and store them.

### Phase 4

Build player stat aggregation and a review screen.

### Phase 5

Improve model quality and region-specific parsing rules.

## Immediate Next Step

Start with a local prototype that:

- takes a video file
- extracts frames every N seconds
- stores frame metadata
- prepares those frames for AI analysis

This is the smallest real foundation for the rest of OWCStats.
