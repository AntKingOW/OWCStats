---
name: owcs-stats-screenshot-parser
description: Parse OWCS broadcast stat-table screenshots into review-ready markdown files and cross-check the visible Week, Day, Match, Game, map, teams, and player rows against the saved OWCStats schedule, result, map, and roster files. Use when Codex is given Overwatch Champions Series scoreboard screenshots and needs to organize them into the established `OWCS_KOREA_2026_WEEK1_DAYX_MATCHY_STATS_REVIEW.md` style.
---

# OWCS Stats Screenshot Parser

Use this skill when the user provides OWCS scoreboard screenshots that show the in-broadcast `GAME DATA` table and wants them turned into structured OWCStats records.

## Workflow

1. Open the supplied screenshots and read the visible overlay fields:
   - `WEEK X DAY Y`
   - `MATCH X GAME Y`
   - map name
   - elapsed time
   - top team / bottom team names or acronyms
2. Cross-check those values against the saved OWCStats files in `C:\Users\user\Documents\Playground\OWCStats`.
3. Use the saved schedule and result files to confirm the expected matchup and map order before trusting the screenshot label blindly.
4. Use the saved roster file to verify the ten observed players and infer the role labels:
   - shield icon = `Tank`
   - gun icon = `DPS`
   - cross icon = `Support`
5. Write or update a review file in the established format used by the existing Week 1 review files.
6. If the supplied material includes result popups, MVP, bans, or map outcomes, update the matching saved result file in the same turn.
7. Every time new stat-table screenshots or result popups are provided, update `C:\Users\user\Documents\Playground\OWCStats\owcstats_current_dashboard.html` in the same turn.
8. Treat the dashboard as required output, not an optional follow-up. If no separate dashboard builder exists, patch the embedded dashboard data directly.
9. If the screenshot overlay conflicts with saved match info, call that out explicitly in an `Overlay alignment` note instead of silently rewriting history.
10. Before any dashboard refresh, canonicalize player names against `TEAM_ROSTERS_2026.md` and merge case-only duplicates such as `BLISS/Bliss`, `SKEWED/skewed`, or `shu/Shu` into the roster-approved spelling.
11. Treat case-only name differences as the same player everywhere in downstream views, charts, and aggregates unless the roster file explicitly distinguishes them.

## Definition Of Done

A screenshot/result turn is complete only when all applicable outputs are updated:

- review markdown file
- saved week result file
- `owcstats_current_dashboard.html`
- canonical player dedupe behavior remains intact

## Project Files To Read

Read these files as needed:

- `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEKS_1_TO_4.md`
- `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEK1_RESULTS.md`
- `C:\Users\user\Documents\Playground\OWCStats\TEAM_ROSTERS_2026.md`
- `C:\Users\user\Documents\Playground\OWCStats\ALL_MAPS.md`

If needed, inspect an existing review file that matches the target format. The most reliable examples live in:

- `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEK1_DAY1_MATCH1_STATS_REVIEW.md`
- `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEK1_DAY2_MATCH1_STATS_REVIEW.md`

## Output Format

Use this exact section order:

1. Title: `# OWCS Korea 2026 Week X Day Y Match Z Stats Review`
2. One-line purpose summary
3. `## Cross-check summary`
4. `### Saved match result reference`
5. `### Roster alignment`
6. `### Overlay alignment`
7. One `## Game N` section per screenshot/game
8. Inside each game section:
   - overlay line
   - map line
   - elapsed time line
   - one `### Team Name` table per team

Each player table must use these columns only:

| Player | Role | E | A | D | DMG | H | MIT |

Keep numbers as integers with comma separators where appropriate.

The downstream dashboard builder will compute per-10 stats and `E/D` automatically.

## Decision Rules

- Prefer the screenshot for player stat values.
- Prefer the saved schedule/results files for expected match order and matchup naming.
- Prefer the roster file for stable team naming and player spelling.
- If the same player appears with different capitalization across screenshots, always keep the roster spelling and merge the stats into one player record.
- Keep player names and team names in English; dashboard localization only changes metric labels.
- If the screenshot uses a longer broadcast team name such as `RODE ONSIDE GAMING`, keep the stored canonical team name in the review file and mention the broadcast variant in the alignment note only if it matters.
- If a player substitution appears between games, record the players exactly as shown and mention the rotation in the roster alignment section.
- Do not invent hidden stats or hero-playtime summaries from the visible hero icon. Treat the shown hero only as a visible-at-capture hint unless the user explicitly asks for hero tracking.

## When A Screenshot Set Is Incomplete

- Still write the file if at least one valid game screenshot is provided.
- Clearly state which games are present.
- Do not fabricate missing games.

## Reference

For the recurring file patterns and existing project conventions, read [references/project-context.md](references/project-context.md).
