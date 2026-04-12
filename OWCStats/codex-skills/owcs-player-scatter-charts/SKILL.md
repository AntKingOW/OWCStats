---
name: owcs-player-scatter-charts
description: Build OWCS Korea player scatter charts from the saved total rate stats markdown. Use when the user asks for support or DPS scatter plots such as DMG/10 vs H/10 or Kills/10 vs DMG/10, and preserve the established chart style, team colors, hover tooltips, bold Arial axis labels, and dynamic axis expansion when values exceed the usual range.
---

# OWCS Player Scatter Charts

Use this skill when the user asks for OWCS Korea player stat scatter charts.

## Source Data

- Read `C:\Users\user\Documents\Playground\OWCStats\OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md`.
- Treat case-only name differences such as `Bliss/BLISS`, `shu/Shu`, or `Secret/SECRET` as the same player and merge them by `team + lowercase player name`.
- Prefer the display spelling from the row with the larger minutes total.

## Output Rules

- Generate the chart file by default.
- Do not create CSV files unless the user explicitly changes this rule in a future request.
- Keep the chart as SVG unless the user asks for another format.
- Use team colors:
  - `ZETA DIVISION` -> `#CEFF00`
  - `Team Falcons` -> `#02BD70`
  - `Crazy Raccoon` -> `#E11919`
  - `T1` -> `#E2012D`
  - `Cheeseburger` -> `#FFBE17`
  - `ONSIDE GAMING` -> `#E2E319`
  - `ZAN Esports` -> `#828493`
  - `Poker Face` -> `#501F64`
  - `New Era` -> `#1A1662`
- Use `Arial` for title, subtitle, axis labels, ticks, legend, and player labels.
- Keep axis labels bold and tick labels bold.
- Show only the player name next to each point unless the user asks for team names too.
- Add an SVG `<title>` tooltip on each point so hover shows `Player: (x_value, y_value)`.
- Use `DMG/10` as the x-axis for all role charts unless the user explicitly asks for a different x-axis.

## Presets

### Support preset

- x-axis: `DMG/10`
- y-axis: `H/10`
- title: `OWCS Korea 2026 Support DMG/10 vs H/10`
- subtitle should state that the points are aggregated from `OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md` and currently cover Weeks 1-2.
- default axis titles:
  - `DAMAGE per 10 min.`
  - `HEALING per 10 min.`
- default axis range:
  - x: `2500` to `6000`
  - y: `5000` to `12000`

### DPS preset

- x-axis: `DMG/10`
- y-axis: `Kills/10`
- title: `OWCS Korea 2026 DPS DMG/10 vs Kills/10`
- subtitle should state that the points are aggregated from `OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md` and currently cover Weeks 1-2.
- default axis titles:
  - `DAMAGE per 10 min.`
  - `KILLS per 10 min.`
- choose a DPS-appropriate default range and keep the style identical to the support chart.

### Tank preset

- x-axis: `DMG/10`
- y-axis: `E/D`
- title: `OWCS Korea 2026 Tank DMG/10 vs E/D`
- subtitle should state that the points are aggregated from `OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md` and currently cover Weeks 1-2.
- default axis titles:
  - `DAMAGE per 10 min.`
  - `KILLS per LIFE`
- choose a tank-appropriate default range and keep the style identical to the support chart.

## Match-Specific Default

- When the user asks for a specific match, prefer one combined SVG dashboard instead of separate role files.
- The dashboard should show three side-by-side panels for `Support`, `DPS`, and `Tank`.
- Do not generate a tank-only match SVG by default.
- For match-specific requests, always return one combined role dashboard that includes all three positions unless the user explicitly overrides this rule.
- Keep the same visual style as the role charts, but size the match dashboard to about 90% of the previous wide layout so it is easier to view in the browser without zooming out as much.
- Replace the usual season subtitle with match context in this format:
  - `Week X Day Y Match Z | Result: Team A score Team B | Winner: Winner Name`
- For match dashboards, keep `DMG/10` on the x-axis in every panel.

## Axis Scaling Rule

- Follow the established default range for the requested chart type when the data fits.
- If any value falls outside that default range, expand the affected axis automatically instead of clipping the point.
- Expand only as much as needed and use clean rounded steps so the ticks stay readable.
- Keep six tick positions from min to max unless the user asks for a different tick layout.

## Recommended Script

- Prefer `C:\Users\user\Documents\Playground\OWCStats\build_owcs_player_scatter.py`.
- Use the support preset for healer charts, the DPS preset for dealer charts, and the tank preset for tank charts.
- If the user asks for a new metric pair, extend the shared script instead of duplicating chart logic.
