# OWCStats Match Info Format

## Purpose

This document defines the first metadata format for OWCS match information.

It is meant for information that can be gathered from sources like Liquipedia before any video analysis starts.

## What This First Format Covers

This format is only for match information.

It does not yet include:

- player combat stats
- kill feed events
- ultimate tracking
- hero swap timing
- per-fight analysis

## Why This Matters

Before analyzing videos, OWCStats should know:

- what event the match belongs to
- which teams played
- when the match happened
- how the series score ended
- what maps were played
- where the VOD can be found

This metadata becomes the backbone for all later player statistics.

## Recommended Match Information Fields

### Tournament-Level Fields

- series_name
- tournament_name
- game_title
- region
- subregion
- stage
- phase
- format_type
- match_format
- timezone
- source_page_url

### Match-Level Fields

- match_id
- match_date
- scheduled_time
- status
- team_1_name
- team_2_name
- winner_name
- loser_name
- series_score
- team_1_map_wins
- team_2_map_wins
- best_of
- week_label
- round_label
- bracket_or_group
- notes

### Map-Level Fields

- map_number
- map_name
- map_mode
- map_winner
- optional_map_score
- map_notes

### Source Fields

- liquipedia_url
- vod_url
- vod_platform
- vod_title
- vod_notes

## Natural Language Input Format

The user can provide information in plain Korean or plain English.

Example:

```text
대회명: OWCS 2026 Korea Stage 1 Regular Season
지역: Korea
단계: Regular Season
경기 날짜: 2026-03-20
주차: Week 1
팀1: Crazy Raccoon
팀2: ZETA DIVISION
결과: Crazy Raccoon 3:1 ZETA DIVISION
맵:
1세트 부산 - Crazy Raccoon 승
2세트 왕의 길 - ZETA DIVISION 승
3세트 뉴 퀸 스트리트 - Crazy Raccoon 승
4세트 리알토 - Crazy Raccoon 승
VOD: 유튜브 링크
비고: 한국 중계 기준
```

## OWCStats Internal Structured Format

```json
{
  "series_name": "Overwatch Champions Series",
  "tournament_name": "OWCS 2026 Korea Stage 1",
  "game_title": "Overwatch 2",
  "region": "Asia",
  "subregion": "Korea",
  "stage": "Stage 1",
  "phase": "Regular Season",
  "format_type": "Round Robin",
  "match_format": "First to 3",
  "timezone": "KST",
  "source_page_url": "https://liquipedia.net/...",
  "match": {
    "match_id": "owcs-2026-korea-s1-rs-weekX-team1-vs-team2",
    "match_date": "2026-03-20",
    "scheduled_time": null,
    "status": "completed",
    "team_1_name": "Team 1",
    "team_2_name": "Team 2",
    "winner_name": "Team 1",
    "loser_name": "Team 2",
    "series_score": "3:1",
    "team_1_map_wins": 3,
    "team_2_map_wins": 1,
    "best_of": 5,
    "week_label": "Week 1",
    "round_label": "Regular Season",
    "bracket_or_group": "Round Robin",
    "notes": "Only store verified results from Liquipedia or manual review"
  },
  "maps": [
    {
      "map_number": 1,
      "map_name": "Map Name 1",
      "map_mode": "Control",
      "map_winner": "Team 1",
      "optional_map_score": null,
      "map_notes": null
    },
    {
      "map_number": 2,
      "map_name": "Map Name 2",
      "map_mode": "Hybrid",
      "map_winner": "Team 2",
      "optional_map_score": null,
      "map_notes": null
    }
  ],
  "sources": {
    "liquipedia_url": "https://liquipedia.net/...",
    "vod_url": "https://youtube.com/...",
    "vod_platform": "YouTube",
    "vod_title": null,
    "vod_notes": null
  }
}
```

## Simple Spreadsheet Columns

If you want to manage this in Excel first, the simplest useful columns are:

- tournament_name
- region
- subregion
- stage
- phase
- week_label
- match_date
- team_1_name
- team_2_name
- winner_name
- series_score
- map_1_name
- map_1_winner
- map_2_name
- map_2_winner
- map_3_name
- map_3_winner
- map_4_name
- map_4_winner
- map_5_name
- map_5_winner
- liquipedia_url
- vod_url
- notes

## What Liquipedia Seems Good For

Based on the OWCS Korea Stage 1 pages, Liquipedia is a strong source for:

- event name
- organizer
- region
- format
- dates
- team names
- standings context
- schedule structure
- map pool
- roster references
- source page links

## What Liquipedia May Not Fully Guarantee

For OWCStats, these items may still need manual confirmation:

- exact VOD timestamp boundaries for each match
- map-by-map winners on every page
- exact player lineup used in that specific match
- substitutions
- observer-side display names in the broadcast

## Recommended Workflow

1. Gather tournament and match metadata from Liquipedia
2. Attach the VOD link
3. Add manual match start and end timestamps from YouTube
4. Add map order if known
5. Use this metadata as the base record before video analysis

## Immediate Practical Rule

If a piece of information is missing, record it as unknown instead of guessing.

Never use illustrative team names or scores as real match data.
