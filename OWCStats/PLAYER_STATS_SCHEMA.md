# OWCStats Player Stats Schema

## Purpose

This document defines the first-pass player stat schema for OWCStats.

The assumption is:

- match results are stored first
- player stats will later be extracted from VODs and screenshots
- actual starting players can be inferred from the broadcast HUD and in-game views

## Core Principle

Player stats should be split into two groups:

1. directly observable stats from video
2. derived stats calculated from stored events

This makes the system easier to build and easier to verify.

## Level 1: Match Participation Data

These fields describe whether a player actually appeared in a match or map.

- team_name
- player_id
- match_date
- week_label
- day_label
- match_order
- map_number
- hero_played
- starting_lineup_status
- map_appearance_status

## Level 2: Directly Observable Event Data

These are the most important raw items to capture from footage.

- eliminations
- deaths
- final_blows
- assists
- solo_kills
- environmental_kills
- hero_swaps
- ultimate_used_count
- first_death_count
- first_elimination_count
- mvp_status

## Level 3: Map Outcome Context

These fields give context to a player's performance on a specific map.

- map_name
- map_mode
- map_winner
- map_score_text
- push_distance_team
- push_distance_opponent
- series_score_at_map_start
- series_score_at_map_end

## Level 4: Hero Usage Data

These fields track hero usage over a match or map.

- hero_name
- hero_time_played_estimate
- hero_start_status
- hero_end_status
- hero_swap_in_timestamp
- hero_swap_out_timestamp
- ultimate_earned_count_estimate

## Level 5: Derived Performance Stats

These should be calculated later from stored raw events.

- kda
- kill_participation
- deaths_per_map
- final_blows_per_map
- first_pick_rate
- first_death_rate
- hero_pool_usage_rate
- map_win_rate_by_hero

## Recommended First Version

Version 1 should stay narrow and practical.

Store these first:

- player_id
- team_name
- map_number
- hero_name
- eliminations
- deaths
- final_blows
- assists
- ultimate_used_count
- hero_swaps

## Why These First

These are the most useful stats that people already expect to see on a public stats site.

They are also more realistic to extract from broadcast footage than advanced hidden metrics.

## Stats To Avoid In Early Versions

Do not try to capture these first:

- exact damage dealt
- healing done
- mitigated damage
- cooldown usage rate
- ability-specific accuracy
- exact ultimate charge percentages

These are much harder to extract reliably from normal broadcast VODs.

## Suggested Storage Levels

### Match-Level Player Summary

One record per player per match.

Useful fields:

- player_id
- team_name
- opponent_team_name
- match_date
- total_maps_played
- total_eliminations
- total_deaths
- total_final_blows
- total_assists
- total_ultimate_used_count

### Map-Level Player Summary

One record per player per map.

Useful fields:

- player_id
- team_name
- map_name
- map_mode
- hero_usage_summary
- eliminations
- deaths
- final_blows
- assists
- ultimate_used_count

### Event-Level Timeline

One record per detected event.

Useful fields:

- timestamp
- player_id
- event_type
- hero_name
- target_player_id
- confidence
- source_type

## Important Verification Rule

If a stat cannot be confidently observed from video, store it as unknown instead of guessing.

## Natural Language Review Format

This is a good human review input style:

```text
3월 20일 Match 2 Map 1
ZETA Proper
영웅: Tracer
처치 14
데스 3
파이널블로우 6
어시스트 4
궁 사용 3
교체 없음
```

## Next Practical Step

After defining this schema, the next step should be:

1. define which of these stats are actually visible in the VOD
2. define how each one is recognized
3. define confidence rules for uncertain detections
