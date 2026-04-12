from __future__ import annotations

import html
from pathlib import Path

from build_owcs_player_scatter import TEAM_COLORS, choose_bounds, format_tick, scale


ROOT = Path(__file__).resolve().parent

# Legacy helper only. For match requests, use build_owcs_match_role_dashboards.py
# and generate the combined Support/DPS/Tank SVG instead of a tank-only file.

MATCH_PRESETS = [
    {
        "slug": "week1_day3_match3_zeta_vs_falcons",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY3_MATCH3_STATS_REVIEW.md",
        "title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "subtitle": "Week 1 Day 3 Match 3 | Result: ZETA DIVISION 3:2 Team Falcons | Winner: ZETA DIVISION",
    },
    {
        "slug": "week1_day1_match2_zeta_vs_raccoon",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md",
        "title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "subtitle": "Week 1 Day 1 Match 2 | Result: ZETA DIVISION 3:1 Crazy Raccoon | Winner: ZETA DIVISION",
    },
    {
        "slug": "week1_day3_match2_onside_vs_t1",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY3_MATCH2_STATS_REVIEW.md",
        "title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "subtitle": "Week 1 Day 3 Match 2 | Result: ONSIDE GAMING 3:2 T1 | Winner: ONSIDE GAMING",
    },
    {
        "slug": "week2_day1_match3_onside_vs_raccoon",
        "review_file": "OWCS_KOREA_2026_WEEK2_DAY1_MATCH3_STATS_REVIEW.md",
        "title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "subtitle": "Week 2 Day 1 Match 3 | Result: Crazy Raccoon 3:2 ONSIDE GAMING | Winner: Crazy Raccoon",
    },
    {
        "slug": "week2_day3_match3_t1_vs_falcons",
        "review_file": "OWCS_KOREA_2026_WEEK2_DAY3_MATCH3_STATS_REVIEW.md",
        "title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "subtitle": "Week 2 Day 3 Match 3 | Result: Team Falcons 3:1 T1 | Winner: Team Falcons",
    },
]


def parse_number(text: str) -> int:
    return int(text.replace(",", "").strip())


def parse_elapsed_minutes(text: str) -> float:
    minutes, seconds = text.split(":")
    return int(minutes) + int(seconds) / 60


def parse_match_tank_rows(path: Path) -> list[dict[str, float | str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    current_team: str | None = None
    current_elapsed_minutes = 0.0
    in_table = False
    rows: list[dict[str, float | str]] = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- Elapsed time:"):
            elapsed_text = stripped.split("`")[1]
            current_elapsed_minutes = parse_elapsed_minutes(elapsed_text)
            continue

        if stripped.startswith("### "):
            current_team = stripped[4:].strip()
            in_table = False
            continue

        if stripped.startswith("| Player | Role |"):
            in_table = True
            continue

        if in_table and stripped.startswith("| ---"):
            continue

        if in_table and stripped.startswith("|"):
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if len(parts) != 8:
                continue
            player, role, e, a, d, dmg, h, mit = parts
            if role != "Tank":
                continue
            rows.append(
                {
                    "team": current_team or "",
                    "player": player,
                    "minutes": current_elapsed_minutes,
                    "elims": parse_number(e),
                    "assists": parse_number(a),
                    "deaths": parse_number(d),
                    "damage": parse_number(dmg),
                    "healing": parse_number(h),
                    "mitigation": parse_number(mit),
                }
            )
            continue

        if in_table and not stripped.startswith("|"):
            in_table = False

    return rows


def aggregate_tank_rows(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str], dict[str, float | str]] = {}

    for row in rows:
        key = (str(row["team"]), str(row["player"]).lower())
        if key not in grouped:
            grouped[key] = {
                "team": row["team"],
                "player": row["player"],
                "minutes": 0.0,
                "elims": 0.0,
                "assists": 0.0,
                "deaths": 0.0,
                "damage": 0.0,
                "healing": 0.0,
                "mitigation": 0.0,
            }

        grouped[key]["minutes"] += float(row["minutes"])
        grouped[key]["elims"] += float(row["elims"])
        grouped[key]["assists"] += float(row["assists"])
        grouped[key]["deaths"] += float(row["deaths"])
        grouped[key]["damage"] += float(row["damage"])
        grouped[key]["healing"] += float(row["healing"])
        grouped[key]["mitigation"] += float(row["mitigation"])

    aggregated: list[dict[str, float | str]] = []
    for row in grouped.values():
        minutes = float(row["minutes"])
        deaths = float(row["deaths"])
        damage = float(row["damage"])
        elims = float(row["elims"])
        aggregated.append(
            {
                "team": row["team"],
                "player": row["player"],
                "maps": int(round(minutes)),
                "minutes": round(minutes, 2),
                "elims": int(round(elims)),
                "assists": int(round(float(row["assists"]))),
                "deaths": int(round(deaths)),
                "damage": int(round(damage)),
                "healing": int(round(float(row["healing"]))),
                "mitigation": int(round(float(row["mitigation"]))),
                "ed_ratio": round(elims / deaths, 2) if deaths else 0.0,
                "dmg_per_10": round(damage / minutes * 10, 2),
            }
        )

    aggregated.sort(key=lambda item: (str(item["team"]), str(item["player"]).lower()))
    return aggregated


def write_svg(rows: list[dict[str, float | str]], path: Path, title: str, subtitle: str) -> None:
    width = 1400
    height = 900
    margin_left = 110
    margin_right = 280
    margin_top = 90
    margin_bottom = 110
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    x_values = [float(row["dmg_per_10"]) for row in rows]
    y_values = [float(row["ed_ratio"]) for row in rows]
    x_min, x_max = choose_bounds(x_values, 5500, 11500, 1000)
    y_min, y_max = choose_bounds(y_values, 0.5, 8.0, 0.5)

    teams = sorted({str(row["team"]) for row in rows})
    team_counts = {team: sum(1 for row in rows if row["team"] == team) for team in teams}

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fafafa" />',
        f'<rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="#ffffff" stroke="#d0d7de" />',
        f'<text x="{margin_left}" y="42" font-family="Arial" font-size="28" font-weight="700" fill="#111827">{html.escape(title)}</text>',
        f'<text x="{margin_left}" y="68" font-family="Arial" font-size="15" fill="#4b5563">{html.escape(subtitle)}</text>',
    ]

    for tick in range(6):
        x_value = x_min + (x_max - x_min) * tick / 5
        y_value = y_min + (y_max - y_min) * tick / 5
        x_pixel = margin_left + plot_width * tick / 5
        y_pixel = margin_top + plot_height - plot_height * tick / 5

        svg_lines.append(f'<line x1="{x_pixel:.2f}" y1="{margin_top}" x2="{x_pixel:.2f}" y2="{margin_top + plot_height}" stroke="#eef2f7" />')
        svg_lines.append(f'<line x1="{margin_left}" y1="{y_pixel:.2f}" x2="{margin_left + plot_width}" y2="{y_pixel:.2f}" stroke="#eef2f7" />')
        svg_lines.append(f'<text x="{x_pixel:.2f}" y="{margin_top + plot_height + 32}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#4b5563">{format_tick(x_value)}</text>')
        svg_lines.append(f'<text x="{margin_left - 16}" y="{y_pixel + 5:.2f}" text-anchor="end" font-family="Arial" font-size="13" font-weight="700" fill="#4b5563">{format_tick(y_value)}</text>')

    svg_lines.append(
        f'<text x="{margin_left + plot_width / 2:.2f}" y="{height - 34}" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#111827">DAMAGE per 10 min.</text>'
    )
    svg_lines.append(
        f'<text x="38" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" transform="rotate(-90 38 {margin_top + plot_height / 2:.2f})" font-family="Arial" font-size="18" font-weight="700" fill="#111827">KILLS per LIFE</text>'
    )

    for row in rows:
        x_value = float(row["dmg_per_10"])
        y_value = float(row["ed_ratio"])
        x = scale(x_value, x_min, x_max, margin_left, margin_left + plot_width)
        y = scale(y_value, y_min, y_max, margin_top + plot_height, margin_top)
        color = TEAM_COLORS.get(str(row["team"]), "#6b7280")
        label = html.escape(str(row["player"]))
        tooltip = html.escape(f'{row["player"]}: ({x_value:.2f}, {y_value:.2f})')
        svg_lines.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" fill="{color}" fill-opacity="0.88" stroke="#ffffff" stroke-width="1.5"><title>{tooltip}</title></circle>'
        )
        svg_lines.append(f'<text x="{x + 10:.2f}" y="{y - 10:.2f}" font-family="Arial" font-size="12" fill="#1f2937">{label}</text>')

    legend_x = margin_left + plot_width + 24
    legend_y = margin_top + 12
    svg_lines.append(f'<text x="{legend_x}" y="{legend_y}" font-family="Arial" font-size="18" font-weight="700" fill="#111827">Teams</text>')
    for index, team in enumerate(teams):
        item_y = legend_y + 28 + index * 26
        color = TEAM_COLORS.get(team, "#6b7280")
        label = html.escape(f"{team} ({team_counts[team]})")
        svg_lines.append(f'<circle cx="{legend_x + 8}" cy="{item_y - 5}" r="6" fill="{color}" />')
        svg_lines.append(f'<text x="{legend_x + 22}" y="{item_y}" font-family="Arial" font-size="13" fill="#374151">{label}</text>')

    svg_lines.append("</svg>")
    path.write_text("\n".join(svg_lines), encoding="utf-8")


def build_match_chart(preset: dict[str, str]) -> Path:
    review_path = ROOT / preset["review_file"]
    rows = aggregate_tank_rows(parse_match_tank_rows(review_path))
    svg_path = ROOT / f'{preset["slug"]}_tank_ed_dmg_scatter.svg'
    write_svg(rows, svg_path, preset["title"], preset["subtitle"])
    return svg_path


def main() -> None:
    for preset in MATCH_PRESETS:
        svg_path = build_match_chart(preset)
        print(f"SVG written: {svg_path}")


if __name__ == "__main__":
    main()
