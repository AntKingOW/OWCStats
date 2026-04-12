from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_HTML_PATH = ROOT / "owcstats_current_dashboard.html"
ROSTER_PATH = ROOT / "TEAM_ROSTERS_2026.md"

TEAM_COLORS = {
    "ZETA DIVISION": "#CEFF00",
    "Team Falcons": "#02BD70",
    "Crazy Raccoon": "#E11919",
    "T1": "#E2012D",
    "Cheeseburger": "#FFBE17",
    "ONSIDE GAMING": "#E2E319",
    "ZAN Esports": "#828493",
    "Poker Face": "#501F64",
    "New Era": "#1A1662",
}

CHART_PRESETS = {
    "support": {
        "role": "Support",
        "x_metric": "dmg_per_10",
        "y_metric": "heal_per_10",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "HEALING per 10 min.",
        "chart_title": "OWCS Korea 2026 Support DMG/10 vs H/10",
        "x_min": 2500,
        "x_max": 6000,
        "x_step": 500,
        "y_min": 5000,
        "y_max": 12000,
        "y_step": 1000,
        "svg_name": "owcs_korea_2026_support_dmg_heal_scatter.svg",
    },
    "dps": {
        "role": "DPS",
        "x_metric": "dmg_per_10",
        "y_metric": "elim_per_10",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "KILLS per 10 min.",
        "chart_title": "OWCS Korea 2026 DPS DMG/10 vs Kills/10",
        "x_min": 6000,
        "x_max": 11000,
        "x_step": 1000,
        "y_min": 5,
        "y_max": 25,
        "y_step": 2,
        "svg_name": "owcs_korea_2026_dps_kill_dmg_scatter.svg",
    },
    "tank": {
        "role": "Tank",
        "x_metric": "dmg_per_10",
        "y_metric": "ed_ratio",
        "x_title": "DAMAGE per 10 min.",
        "y_title": "KILLS per LIFE",
        "chart_title": "OWCS Korea 2026 Tank DMG/10 vs E/D",
        "x_min": 5500,
        "x_max": 11500,
        "x_step": 1000,
        "y_min": 0.5,
        "y_max": 8.0,
        "y_step": 0.5,
        "svg_name": "owcs_korea_2026_tank_ed_dmg_scatter.svg",
    },
}


def parse_number(text: str) -> float:
    return float(text.replace(",", "").strip())


def load_period_rows() -> tuple[dict[str, list[dict[str, object]]], list[str]]:
    raw = SOURCE_HTML_PATH.read_text(encoding="utf-8")
    match = re.search(r"const PERIOD_ROWS = (\{.*?\});", raw, re.DOTALL)
    if not match:
        raise RuntimeError("PERIOD_ROWS block not found in owcstats_current_dashboard.html")
    data = json.loads(match.group(1))
    active_periods = [period for period, rows in data.items() if rows]
    return data, active_periods


def load_roster_names() -> dict[tuple[str, str], str]:
    raw = ROSTER_PATH.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\[.*?\])\s*```", raw, re.DOTALL)
    if not match:
        return {}
    records = json.loads(match.group(1))
    canonical: dict[tuple[str, str], str] = {}
    for record in records:
        team = str(record["team_name"])
        player = str(record["player_id"])
        canonical[(team, player.lower())] = player
    return canonical


def format_period_label(active_periods: list[str]) -> str:
    week_numbers = sorted(
        int(period.split()[1])
        for period in active_periods
        if period.startswith("Week ") and len(period.split()) == 2
    )
    has_playoff = "Playoff" in active_periods

    parts: list[str] = []
    if week_numbers:
        if week_numbers == list(range(1, week_numbers[-1] + 1)):
            parts.append(f"Weeks 1-{week_numbers[-1]}")
        else:
            joined = ", ".join(str(number) for number in week_numbers)
            parts.append(f"Weeks {joined}")
    if has_playoff:
        parts.append("Playoffs")
    return " + ".join(parts) if parts else "all available periods"


def build_subtitle(role: str, active_periods: list[str]) -> str:
    role_label = role.lower()
    period_label = format_period_label(active_periods)
    return (
        f"Each point is a {role_label} player aggregated from "
        f"owcstats_current_dashboard.html covering {period_label}."
    )


def load_rows(role: str, canonical_names: dict[tuple[str, str], str]) -> list[dict[str, str | float]]:
    period_rows, _ = load_period_rows()
    data_rows: list[dict[str, str | float]] = []

    for period_name, rows in period_rows.items():
        if period_name == "Playoff":
            continue
        for row in rows:
            if str(row["Role"]) != role:
                continue
            team = str(row["Team"])
            raw_player = str(row["Player"])
            canonical_player = canonical_names.get((team, raw_player.lower()), raw_player)
            data_rows.append(
                {
                    "team": team,
                    "player": canonical_player,
                    "role": str(row["Role"]),
                    "appearances": str(row["Appearances"]),
                    "minutes": str(row["Minutes"]),
                    "elims": str(row["E"]),
                    "assists": str(row["A"]),
                    "deaths": str(row["D"]),
                    "damage": str(row["DMG"]),
                    "healing": str(row["H"]),
                    "mitigation": str(row["MIT"]),
                }
            )

    return data_rows


def normalize_rows(rows: list[dict[str, str | float]]) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str], dict[str, float | str]] = {}
    display_names: dict[tuple[str, str], tuple[str, float]] = {}

    for row in rows:
        key = (row["team"], row["player"].lower())
        minutes = parse_number(row["minutes"])

        if key not in grouped:
            grouped[key] = {
                "team": row["team"],
                "player": row["player"],
                "appearances": 0.0,
                "minutes": 0.0,
                "elims": 0.0,
                "assists": 0.0,
                "deaths": 0.0,
                "damage": 0.0,
                "healing": 0.0,
                "mitigation": 0.0,
            }

        if key not in display_names or minutes > display_names[key][1]:
            display_names[key] = (row["player"], minutes)

        grouped[key]["appearances"] += parse_number(row["appearances"])
        grouped[key]["minutes"] += minutes
        grouped[key]["elims"] += parse_number(row["elims"])
        grouped[key]["assists"] += parse_number(row["assists"])
        grouped[key]["deaths"] += parse_number(row["deaths"])
        grouped[key]["damage"] += parse_number(row["damage"])
        grouped[key]["healing"] += parse_number(row["healing"])
        grouped[key]["mitigation"] += parse_number(row["mitigation"])

    normalized_rows: list[dict[str, float | str]] = []
    for key, row in grouped.items():
        minutes = float(row["minutes"])
        deaths = float(row["deaths"])
        player_name = display_names[key][0]
        elims = float(row["elims"])
        damage = float(row["damage"])
        healing = float(row["healing"])
        mitigation = float(row["mitigation"])
        assists = float(row["assists"])

        normalized_rows.append(
            {
                "team": row["team"],
                "player": player_name,
                "appearances": int(round(float(row["appearances"]))),
                "minutes": round(minutes, 2),
                "elims": int(round(elims)),
                "assists": int(round(assists)),
                "deaths": int(round(deaths)),
                "damage": int(round(damage)),
                "healing": int(round(healing)),
                "mitigation": int(round(mitigation)),
                "elim_per_10": round(elims / minutes * 10, 2),
                "assist_per_10": round(assists / minutes * 10, 2),
                "death_per_10": round(deaths / minutes * 10, 2),
                "dmg_per_10": round(damage / minutes * 10, 2),
                "heal_per_10": round(healing / minutes * 10, 2),
                "mit_per_10": round(mitigation / minutes * 10, 2),
                "ed_ratio": round(elims / deaths, 2) if deaths else 0.0,
            }
        )

    normalized_rows.sort(key=lambda item: (str(item["team"]), str(item["player"]).lower()))
    return normalized_rows


def choose_bounds(values: list[float], axis_min: float, axis_max: float, step: float) -> tuple[float, float]:
    data_min = min(values)
    data_max = max(values)
    chosen_min = axis_min
    chosen_max = axis_max

    if data_min < axis_min:
        units = int((axis_min - data_min + step - 1) // step)
        chosen_min = axis_min - units * step

    if data_max > axis_max:
        units = int((data_max - axis_max + step - 1) // step)
        chosen_max = axis_max + units * step

    return chosen_min, chosen_max


def scale(value: float, data_min: float, data_max: float, pixel_min: float, pixel_max: float) -> float:
    if data_max == data_min:
        return (pixel_min + pixel_max) / 2
    ratio = (value - data_min) / (data_max - data_min)
    return pixel_min + ratio * (pixel_max - pixel_min)


def format_tick(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.1f}"


def write_svg(rows: list[dict[str, float | str]], svg_path: Path, config: dict[str, object]) -> None:
    width = 1400
    height = 900
    margin_left = 110
    margin_right = 280
    margin_top = 90
    margin_bottom = 110
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    x_metric = str(config["x_metric"])
    y_metric = str(config["y_metric"])
    x_values = [float(row[x_metric]) for row in rows]
    y_values = [float(row[y_metric]) for row in rows]
    x_min, x_max = choose_bounds(x_values, float(config["x_min"]), float(config["x_max"]), float(config["x_step"]))
    y_min, y_max = choose_bounds(y_values, float(config["y_min"]), float(config["y_max"]), float(config["y_step"]))

    team_counts = defaultdict(int)
    for row in rows:
        team_counts[str(row["team"])] += 1

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fafafa" />',
        f'<rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="#ffffff" stroke="#d0d7de" />',
        f'<text x="{margin_left}" y="42" font-family="Arial" font-size="28" font-weight="700" fill="#111827">{html.escape(str(config["chart_title"]))}</text>',
        f'<text x="{margin_left}" y="68" font-family="Arial" font-size="15" fill="#4b5563">{html.escape(str(config["subtitle"]))}</text>',
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
        f'<text x="{margin_left + plot_width / 2:.2f}" y="{height - 34}" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#111827">{html.escape(str(config["x_title"]))}</text>'
    )
    svg_lines.append(
        f'<text x="38" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" transform="rotate(-90 38 {margin_top + plot_height / 2:.2f})" font-family="Arial" font-size="18" font-weight="700" fill="#111827">{html.escape(str(config["y_title"]))}</text>'
    )

    for row in rows:
        x_value = float(row[x_metric])
        y_value = float(row[y_metric])
        x = scale(x_value, x_min, x_max, margin_left, margin_left + plot_width)
        y = scale(y_value, y_min, y_max, margin_top + plot_height, margin_top)
        label = html.escape(str(row["player"]))
        color = TEAM_COLORS.get(str(row["team"]), "#6b7280")
        tooltip = f"{row['player']}: ({x_value:.2f}, {y_value:.2f})"

        svg_lines.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" fill="{color}" fill-opacity="0.88" stroke="#ffffff" stroke-width="1.5"><title>{html.escape(tooltip)}</title></circle>'
        )
        svg_lines.append(
            f'<text x="{x + 10:.2f}" y="{y - 10:.2f}" font-family="Arial" font-size="12" fill="#1f2937">{label}</text>'
        )

    legend_x = margin_left + plot_width + 24
    legend_y = margin_top + 12
    svg_lines.append(f'<text x="{legend_x}" y="{legend_y}" font-family="Arial" font-size="18" font-weight="700" fill="#111827">Teams</text>')

    for index, team in enumerate(sorted({str(row["team"]) for row in rows})):
        item_y = legend_y + 28 + index * 26
        color = TEAM_COLORS.get(team, "#6b7280")
        label = html.escape(f"{team} ({team_counts[team]})")
        svg_lines.append(f'<circle cx="{legend_x + 8}" cy="{item_y - 5}" r="6" fill="{color}" />')
        svg_lines.append(f'<text x="{legend_x + 22}" y="{item_y}" font-family="Arial" font-size="13" fill="#374151">{label}</text>')

    svg_lines.append("</svg>")
    svg_path.write_text("\n".join(svg_lines), encoding="utf-8")


def build_chart(preset_name: str) -> tuple[Path, int]:
    config = CHART_PRESETS[preset_name]
    canonical_names = load_roster_names()
    _, active_periods = load_period_rows()
    config = dict(config)
    config["subtitle"] = build_subtitle(str(config["role"]), active_periods)
    rows = normalize_rows(load_rows(str(config["role"]), canonical_names))
    svg_path = ROOT / str(config["svg_name"])
    write_svg(rows, svg_path, config)
    return svg_path, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=sorted(CHART_PRESETS), required=True)
    args = parser.parse_args()

    svg_path, row_count = build_chart(args.preset)
    print(f"SVG written: {svg_path}")
    print(f"Players: {row_count}")


if __name__ == "__main__":
    main()
