# OWCStats Project Context

## Canonical Project Files

- Schedule baseline: `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEKS_1_TO_4.md`
- Week 1 results and map order: `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_WEEK1_RESULTS.md`
- Team rosters: `C:\Users\user\Documents\Playground\OWCStats\TEAM_ROSTERS_2026.md`
- Map catalog: `C:\Users\user\Documents\Playground\OWCStats\ALL_MAPS.md`

## Existing Review File Pattern

The project already uses one review file per match:

- `OWCS_KOREA_2026_WEEK1_DAY1_MATCH1_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY1_MATCH3_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY2_MATCH1_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY2_MATCH2_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY2_MATCH3_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY3_MATCH1_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY3_MATCH2_STATS_REVIEW.md`
- `OWCS_KOREA_2026_WEEK1_DAY3_MATCH3_STATS_REVIEW.md`

## Screenshot Parsing Conventions

- Read `Week`, `Day`, `Match`, `Game`, `Map`, and `Elapsed time` from the screenshot overlay first.
- Cross-check the screenshot against the canonical files before finalizing the heading or alignment note.
- Use roster names exactly as stored in the roster file unless the screenshot shows a clearly corrected spelling and the user wants that standardized.
- Use role names in English in the tables: `Tank`, `DPS`, `Support`.
- Keep the existing markdown table structure so the aggregate scripts can parse it later.
- After each screenshot-driven stats update, rebuild `C:\Users\user\Documents\Playground\OWCStats\owcstats_current_dashboard.html` with:
  - `python C:\Users\user\Documents\Playground\OWCStats\build_current_stats_dashboard.py`
- The dashboard build computes period aggregates, `/10` metrics, and `E/D` where:
  - `E/D = E / (D + 1)`
- Dashboard localization may translate metric labels, but player names and team names stay in English.

## Common Cross-Check Outcomes

- Perfect alignment: state that screenshots align with the stored map order.
- Broadcast variant naming: note the variant but keep the canonical team name in the review file.
- Overlay conflict: mention the visible overlay and the saved expected match/game info, then proceed carefully rather than assuming one side is always right.
