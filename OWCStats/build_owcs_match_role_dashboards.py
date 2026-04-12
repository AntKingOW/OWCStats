from __future__ import annotations

import html
from pathlib import Path

from build_owcs_player_scatter import TEAM_COLORS, choose_bounds, format_tick, scale


ROOT = Path(__file__).resolve().parent

MATCH_PRESETS = [
    {
        "slug": "week1_day3_match3_zeta_vs_falcons_roles_dashboard",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY3_MATCH3_STATS_REVIEW.md",
        "subtitle": "Week 1 Day 3 Match 3 | Result: ZETA DIVISION 3:2 Team Falcons | Winner: ZETA DIVISION",
    },
    {
        "slug": "week1_day1_match2_zeta_vs_raccoon_roles_dashboard",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md",
        "subtitle": "Week 1 Day 1 Match 2 | Result: ZETA DIVISION 3:1 Crazy Raccoon | Winner: ZETA DIVISION",
    },
    {
        "slug": "week1_day3_match2_onside_vs_t1_roles_dashboard",
        "review_file": "OWCS_KOREA_2026_WEEK1_DAY3_MATCH2_STATS_REVIEW.md",
        "subtitle": "Week 1 Day 3 Match 2 | Result: ONSIDE GAMING 3:2 T1 | Winner: ONSIDE GAMING",
    },
    {
        "slug": "week2_day1_match3_onside_vs_raccoon_roles_dashboard",
        "review_file": "OWCS_KOREA_2026_WEEK2_DAY1_MATCH3_STATS_REVIEW.md",
        "subtitle": "Week 2 Day 1 Match 3 | Result: Crazy Raccoon 3:2 ONSIDE GAMING | Winner: Crazy Raccoon",
    },
    {
        "slug": "week2_day3_match3_t1_vs_falcons_roles_dashboard",
        "review_file": "OWCS_KOREA_2026_WEEK2_DAY3_MATCH3_STATS_REVIEW.md",
        "subtitle": "Week 2 Day 3 Match 3 | Result: Team Falcons 3:1 T1 | Winner: Team Falcons",
    },
]

ROLE_CONFIGS = {
    "Support": {
        "panel_title": "Support DMG/10 vs H/10",
        "x_metric": "dmg_per_10",
        "y_metric": "heal_per_10",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "HEALING per 10 min.",
        "x_min": 2500,
        "x_max": 6000,
        "x_step": 500,
        "y_min": 5000,
        "y_max": 12000,
        "y_step": 1000,
    },
    "DPS": {
        "panel_title": "DPS DMG/10 vs Kills/10",
        "x_metric": "dmg_per_10",
        "y_metric": "elim_per_10",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "KILLS per 10 min.",
        "x_min": 6000,
        "x_max": 11000,
        "x_step": 1000,
        "y_min": 10,
        "y_max": 30,
        "y_step": 2,
    },
    "Tank": {
        "panel_title": "Tank DMG/10 vs E/D",
        "x_metric": "dmg_per_10",
        "y_metric": "ed_ratio",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "KILLS per LIFE",
        "x_min": 5500,
        "x_max": 11500,
        "x_step": 1000,
        "y_min": 0.5,
        "y_max": 8.0,
        "y_step": 0.5,
    },
}


def parse_number(text: str) -> int:
    return int(text.replace(",", "").strip())


def parse_elapsed_minutes(text: str) -> float:
    minutes, seconds = text.split(":")
    return int(minutes) + int(seconds) / 60


def parse_match_rows(path: Path) -> list[dict[str, float | str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, float | str]] = []
    current_team: str | None = None
    current_elapsed_minutes = 0.0
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- Elapsed time:"):
            current_elapsed_minutes = parse_elapsed_minutes(stripped.split("`")[1])
            continue

        if stripped.startswith("### "):
            current_team = stripped[4:].strip()
            in_table = False
            continue

        if stripped.startswith("| Player | Role |"):
            in_table = True
            continue

        if in_table and "---" in stripped:
            continue

        if in_table and stripped.startswith("|"):
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if len(parts) != 8:
                continue
            player, role, e, a, d, dmg, h, mit = parts
            rows.append(
                {
                    "team": current_team or "",
                    "player": player,
                    "role": role,
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


def aggregate_role_rows(rows: list[dict[str, float | str]], role: str) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str], dict[str, float | str]] = {}

    for row in rows:
        if row["role"] != role:
            continue
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
        elims = float(row["elims"])
        damage = float(row["damage"])
        healing = float(row["healing"])
        aggregated.append(
            {
                "team": row["team"],
                "player": row["player"],
                "minutes": round(minutes, 2),
                "elims": int(round(elims)),
                "assists": int(round(float(row["assists"]))),
                "deaths": int(round(deaths)),
                "damage": int(round(damage)),
                "healing": int(round(healing)),
                "mitigation": int(round(float(row["mitigation"]))),
                "elim_per_10": round(elims / minutes * 10, 2),
                "dmg_per_10": round(damage / minutes * 10, 2),
                "heal_per_10": round(healing / minutes * 10, 2),
                "ed_ratio": round(elims / deaths, 2) if deaths else 0.0,
            }
        )

    aggregated.sort(key=lambda item: (str(item["team"]), str(item["player"]).lower()))
    return aggregated


def draw_panel(
    svg_lines: list[str],
    rows: list[dict[str, float | str]],
    config: dict[str, float | str],
    panel_x: int,
    panel_y: int,
    panel_width: int,
    panel_height: int,
) -> None:
    margin_left = 90
    margin_right = 30
    margin_top = 60
    margin_bottom = 90

    plot_x = panel_x + margin_left
    plot_y = panel_y + margin_top
    plot_width = panel_width - margin_left - margin_right
    plot_height = panel_height - margin_top - margin_bottom

    x_metric = str(config["x_metric"])
    y_metric = str(config["y_metric"])
    x_values = [float(row[x_metric]) for row in rows]
    y_values = [float(row[y_metric]) for row in rows]
    x_min, x_max = choose_bounds(x_values, float(config["x_min"]), float(config["x_max"]), float(config["x_step"]))
    y_min, y_max = choose_bounds(y_values, float(config["y_min"]), float(config["y_max"]), float(config["y_step"]))

    svg_lines.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="10" fill="#ffffff" stroke="#d0d7de" />')
    svg_lines.append(f'<text x="{panel_x + margin_left}" y="{panel_y + 34}" font-family="Arial" font-size="22" font-weight="700" fill="#111827">{html.escape(str(config["panel_title"]))}</text>')

    for tick in range(6):
        x_value = x_min + (x_max - x_min) * tick / 5
        y_value = y_min + (y_max - y_min) * tick / 5
        x_pixel = plot_x + plot_width * tick / 5
        y_pixel = plot_y + plot_height - plot_height * tick / 5

        svg_lines.append(f'<line x1="{x_pixel:.2f}" y1="{plot_y}" x2="{x_pixel:.2f}" y2="{plot_y + plot_height}" stroke="#eef2f7" />')
        svg_lines.append(f'<line x1="{plot_x}" y1="{y_pixel:.2f}" x2="{plot_x + plot_width}" y2="{y_pixel:.2f}" stroke="#eef2f7" />')
        svg_lines.append(f'<text x="{x_pixel:.2f}" y="{plot_y + plot_height + 32}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#4b5563">{format_tick(x_value)}</text>')
        svg_lines.append(f'<text x="{plot_x - 14}" y="{y_pixel + 5:.2f}" text-anchor="end" font-family="Arial" font-size="13" font-weight="700" fill="#4b5563">{format_tick(y_value)}</text>')

    svg_lines.append(f'<text x="{plot_x + plot_width / 2:.2f}" y="{panel_y + panel_height - 18}" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#111827">{html.escape(str(config["x_title"]))}</text>')
    svg_lines.append(f'<text x="{panel_x + 24}" y="{plot_y + plot_height / 2:.2f}" text-anchor="middle" transform="rotate(-90 {panel_x + 24} {plot_y + plot_height / 2:.2f})" font-family="Arial" font-size="18" font-weight="700" fill="#111827">{html.escape(str(config["y_title"]))}</text>')

    for row in rows:
        x_value = float(row[x_metric])
        y_value = float(row[y_metric])
        x = scale(x_value, x_min, x_max, plot_x, plot_x + plot_width)
        y = scale(y_value, y_min, y_max, plot_y + plot_height, plot_y)
        color = TEAM_COLORS.get(str(row["team"]), "#6b7280")
        label = html.escape(str(row["player"]))
        tooltip = html.escape(f'{row["player"]}: ({x_value:.2f}, {y_value:.2f})')
        svg_lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" fill="{color}" fill-opacity="0.88" stroke="#ffffff" stroke-width="1.5"><title>{tooltip}</title></circle>')
        svg_lines.append(f'<text x="{x + 10:.2f}" y="{y - 10:.2f}" font-family="Arial" font-size="12" fill="#1f2937">{label}</text>')


def build_dashboard(preset: dict[str, str]) -> Path:
    rows = parse_match_rows(ROOT / preset["review_file"])
    role_rows = {role: aggregate_role_rows(rows, role) for role in ROLE_CONFIGS}

    width = 1890
    height = 738
    panel_width = 576
    panel_height = 558
    gap = 27
    panel_y = 126
    first_panel_x = 32

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f5f7fb" />',
        '<text x="32" y="43" font-family="Arial" font-size="29" font-weight="700" fill="#111827">OWCS Korea 2026 Match Role Scatter Dashboard</text>',
        f'<text x="32" y="74" font-family="Arial" font-size="16" fill="#4b5563">{html.escape(preset["subtitle"])}</text>',
    ]

    for index, role in enumerate(["Support", "DPS", "Tank"]):
        panel_x = first_panel_x + index * (panel_width + gap)
        draw_panel(svg_lines, role_rows[role], ROLE_CONFIGS[role], panel_x, panel_y, panel_width, panel_height)

    teams = sorted({str(row["team"]) for row in rows})
    legend_x = 32
    legend_y = 711
    svg_lines.append(f'<text x="{legend_x}" y="{legend_y}" font-family="Arial" font-size="16" font-weight="700" fill="#111827">Teams</text>')
    for index, team in enumerate(teams):
        item_x = legend_x + 81 + index * 189
        color = TEAM_COLORS.get(team, "#6b7280")
        svg_lines.append(f'<circle cx="{item_x}" cy="{legend_y - 5}" r="6" fill="{color}" />')
        svg_lines.append(f'<text x="{item_x + 14}" y="{legend_y}" font-family="Arial" font-size="13" fill="#374151">{html.escape(team)}</text>')

    svg_lines.append("</svg>")

    output_path = ROOT / f'{preset["slug"]}.svg'
    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    return output_path


def main() -> None:
    for preset in MATCH_PRESETS:
        output_path = build_dashboard(preset)
        print(f"SVG written: {output_path}")


if __name__ == "__main__":
    main()
