import re
from collections import defaultdict
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
MIN_RANKING_MINUTES = 60.0

REVIEW_FILES = [
    ("Day 1 Match 1", BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH1_STATS_REVIEW.md"),
    ("Day 1 Match 2", BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md"),
    ("Day 1 Match 3", BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH3_STATS_REVIEW.md"),
    ("Day 2 Match 1", BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH1_STATS_REVIEW.md"),
    ("Day 2 Match 2", BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH2_STATS_REVIEW.md"),
    ("Day 2 Match 3", BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH3_STATS_REVIEW.md"),
    ("Day 3 Match 1", BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH1_STATS_REVIEW.md"),
    ("Day 3 Match 2", BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH2_STATS_REVIEW.md"),
    ("Day 3 Match 3", BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH3_STATS_REVIEW.md"),
]

KNOWN_TEAMS = {
    "Cheeseburger",
    "Poker Face",
    "Crazy Raccoon",
    "ZETA DIVISION",
    "ZAN Esports",
    "ONSIDE GAMING",
    "New Era",
    "T1",
    "Team Falcons",
}


def parse_elapsed_to_minutes(text: str) -> float:
    minutes, seconds = text.split(":")
    return int(minutes) + int(seconds) / 60.0


def fmt_num(number: int) -> str:
    return f"{number:,}"


def fmt_rate(value: float) -> str:
    return f"{value:.2f}"


def parse_tables(file_path: Path) -> dict:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    data = {"games": []}
    i = 0
    current_game = None

    while i < len(lines):
        line = lines[i]
        game_match = re.match(r"## (?:Game|Screenshot) (\d+)", line)
        if game_match:
            current_game = {"game_number": int(game_match.group(1)), "teams": {}}
            data["games"].append(current_game)
            i += 1
            continue

        if current_game:
            elapsed_match = re.match(r"- Elapsed time: `([^`]+)`", line)
            if elapsed_match:
                current_game["elapsed_time"] = elapsed_match.group(1)
                current_game["elapsed_minutes"] = parse_elapsed_to_minutes(
                    elapsed_match.group(1)
                )
                i += 1
                continue

            team_match = re.match(r"### (.+)", line)
            if team_match:
                team_name = team_match.group(1).strip()
                if team_name in KNOWN_TEAMS:
                    current_game["teams"][team_name] = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith("| Player |"):
                        i += 1
                    if i < len(lines) and lines[i].startswith("| Player |"):
                        i += 1
                    if i < len(lines) and lines[i].startswith("| ---"):
                        i += 1
                    while i < len(lines) and lines[i].startswith("| "):
                        cols = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                        if len(cols) == 8:
                            player, role, e, a, d, dmg, h, mit = cols
                            current_game["teams"][team_name].append(
                                {
                                    "player": player,
                                    "role": role,
                                    "E": int(e.replace(",", "")),
                                    "A": int(a.replace(",", "")),
                                    "D": int(d.replace(",", "")),
                                    "DMG": int(dmg.replace(",", "")),
                                    "H": int(h.replace(",", "")),
                                    "MIT": int(mit.replace(",", "")),
                                }
                            )
                        i += 1
                    continue
        i += 1

    return data


def build_aggregate(match_data: dict) -> dict:
    aggregate = defaultdict(
        lambda: {
            "team": "",
            "role": "",
            "minutes": 0.0,
            "E": 0,
            "A": 0,
            "D": 0,
            "DMG": 0,
            "H": 0,
            "MIT": 0,
        }
    )

    for game in match_data["games"]:
        minutes = game["elapsed_minutes"]
        for team_name, players in game["teams"].items():
            for player in players:
                row = aggregate[player["player"]]
                row["team"] = team_name
                row["role"] = player["role"]
                row["minutes"] += minutes
                for stat in ("E", "A", "D", "DMG", "H", "MIT"):
                    row[stat] += player[stat]
    return aggregate


def build_week_aggregate(parsed_sections: list[tuple[str, dict]]) -> dict:
    aggregate = defaultdict(
        lambda: {
            "team": "",
            "role": "",
            "minutes": 0.0,
            "E": 0,
            "A": 0,
            "D": 0,
            "DMG": 0,
            "H": 0,
            "MIT": 0,
        }
    )

    for _, match_data in parsed_sections:
        for game in match_data["games"]:
            minutes = game["elapsed_minutes"]
            for team_name, players in game["teams"].items():
                for player in players:
                    row = aggregate[player["player"]]
                    row["team"] = team_name
                    row["role"] = player["role"]
                    row["minutes"] += minutes
                    for stat in ("E", "A", "D", "DMG", "H", "MIT"):
                        row[stat] += player[stat]
    return aggregate


def append_table(lines: list[str], aggregate: dict) -> None:
    lines.extend(
        [
            "| Player | Team | Role | Minutes | E | A | D | DMG | H | MIT | E/min | A/min | D/min | DMG/min | H/min | MIT/min | E/10 | A/10 | D/10 | DMG/10 | H/10 | MIT/10 |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for player in sorted(aggregate):
        row = aggregate[player]
        minutes = row["minutes"]
        e_pm = row["E"] / minutes
        a_pm = row["A"] / minutes
        d_pm = row["D"] / minutes
        dmg_pm = row["DMG"] / minutes
        h_pm = row["H"] / minutes
        mit_pm = row["MIT"] / minutes
        lines.append(
            "| {player} | {team} | {role} | {minutes} | {E} | {A} | {D} | {DMG} | {H} | {MIT} | {e_pm} | {a_pm} | {d_pm} | {dmg_pm} | {h_pm} | {mit_pm} | {e10} | {a10} | {d10} | {dmg10} | {h10} | {mit10} |".format(
                player=player,
                team=row["team"],
                role=row["role"],
                minutes=fmt_rate(minutes),
                E=fmt_num(row["E"]),
                A=fmt_num(row["A"]),
                D=fmt_num(row["D"]),
                DMG=fmt_num(row["DMG"]),
                H=fmt_num(row["H"]),
                MIT=fmt_num(row["MIT"]),
                e_pm=fmt_rate(e_pm),
                a_pm=fmt_rate(a_pm),
                d_pm=fmt_rate(d_pm),
                dmg_pm=fmt_rate(dmg_pm),
                h_pm=fmt_rate(h_pm),
                mit_pm=fmt_rate(mit_pm),
                e10=fmt_rate(e_pm * 10),
                a10=fmt_rate(a_pm * 10),
                d10=fmt_rate(d_pm * 10),
                dmg10=fmt_rate(dmg_pm * 10),
                h10=fmt_rate(h_pm * 10),
                mit10=fmt_rate(mit_pm * 10),
            )
        )


def build_week_rate_markdown(parsed_sections: list[tuple[str, dict]]) -> str:
    lines = [
        "# OWCS Korea 2026 Week 1 Player Rate Stats",
        "",
        "This file aggregates all confirmed Week 1 Day 1-3 player stat screenshots and computes player totals, per-minute rates, and per-10-minute rates using each player's total time played in the captured games.",
        "",
        "Rate calculation rule:",
        "- `per minute = total stat / total minutes played`",
        "- `per 10 minutes = per minute * 10`",
        "",
        "Time source:",
        "- the `Elapsed time` shown on each supplied game-data screenshot",
        "",
    ]

    for section_label, match_data in parsed_sections:
        total_minutes = sum(game["elapsed_minutes"] for game in match_data["games"])
        lines.extend(
            [
                f"## {section_label}",
                "",
                f"- Games captured: `{len(match_data['games'])}`",
                f"- Total combined game time: `{total_minutes:.2f} minutes`",
                "",
            ]
        )
        append_table(lines, build_aggregate(match_data))
        lines.append("")

    lines.extend(["## Week 1 Overall", ""])
    append_table(lines, build_week_aggregate(parsed_sections))
    lines.append("")
    return "\n".join(lines)


def build_role_top5_markdown(week_aggregate: dict) -> str:
    lines = [
        "# OWCS Korea 2026 Week 1 Role Top 5 Rankings",
        "",
        f"This file ranks the top 5 players in Week 1 by role for `DMG/10`, `H/10`, and `MIT/10` using the confirmed screenshot totals and captured game times.",
        "",
        f"Ranking eligibility:",
        f"- players must have at least `{MIN_RANKING_MINUTES:.0f}` total minutes played in Week 1",
        "",
    ]

    role_order = ["Tank", "DPS", "Support"]
    metric_map = [("DMG", "DMG/10"), ("H", "H/10"), ("MIT", "MIT/10")]

    for role in role_order:
        lines.extend([f"## {role}", ""])
        role_rows = []
        for player, row in week_aggregate.items():
            if row["role"] == role:
                role_rows.append(
                    {
                        "player": player,
                        "team": row["team"],
                        "minutes": row["minutes"],
                        "DMG/10": (row["DMG"] / row["minutes"]) * 10,
                        "H/10": (row["H"] / row["minutes"]) * 10,
                        "MIT/10": (row["MIT"] / row["minutes"]) * 10,
                    }
                )

        for _, label in metric_map:
            lines.extend(
                [
                    f"### {label} Top 5",
                    "",
                    "| Rank | Player | Team | Minutes | Value |",
                    "| ---: | --- | --- | ---: | ---: |",
                ]
            )
            ranked = sorted(
                [
                    item
                    for item in role_rows
                    if item["minutes"] >= MIN_RANKING_MINUTES
                ],
                key=lambda item: (-item[label], item["player"].lower()),
            )[:5]
            for rank, row in enumerate(ranked, start=1):
                lines.append(
                    f"| {rank} | {row['player']} | {row['team']} | {fmt_rate(row['minutes'])} | {fmt_rate(row[label])} |"
                )
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    parsed_sections = [(label, parse_tables(path)) for label, path in REVIEW_FILES]
    week_rates = build_week_rate_markdown(parsed_sections)
    week_aggregate = build_week_aggregate(parsed_sections)
    role_top5 = build_role_top5_markdown(week_aggregate)

    (BASE / "OWCS_KOREA_2026_WEEK1_PLAYER_RATE_STATS.md").write_text(
        week_rates, encoding="utf-8"
    )
    (BASE / "OWCS_KOREA_2026_WEEK1_ROLE_TOP5.md").write_text(
        role_top5, encoding="utf-8"
    )

    print(BASE / "OWCS_KOREA_2026_WEEK1_PLAYER_RATE_STATS.md")
    print(BASE / "OWCS_KOREA_2026_WEEK1_ROLE_TOP5.md")


if __name__ == "__main__":
    main()
