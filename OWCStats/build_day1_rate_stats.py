import re
from collections import defaultdict
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")

MATCH_FILES = {
    1: BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH1_STATS_REVIEW.md",
    2: BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md",
    3: BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH3_STATS_REVIEW.md",
}

MATCH_LABELS = {
    1: "Cheeseburger vs Poker Face",
    2: "Crazy Raccoon vs ZETA DIVISION",
    3: "ZAN Esports vs ONSIDE GAMING",
}


def parse_elapsed_to_minutes(text: str) -> float:
    minutes, seconds = text.split(":")
    return int(minutes) + (int(seconds) / 60.0)


def parse_tables(file_path: Path) -> dict:
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()
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

            team_heading = re.match(r"### (.+)", line)
            if team_heading:
                team_name = team_heading.group(1).strip()
                # Skip non-team headings if any appear inside game body
                if team_name in {
                    "Cheeseburger",
                    "Poker Face",
                    "Crazy Raccoon",
                    "ZETA DIVISION",
                    "ZAN Esports",
                    "ONSIDE GAMING",
                }:
                    current_game["teams"][team_name] = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith("| Player |"):
                        i += 1
                    # Skip header + separator lines if present
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


def fmt_num(n: int) -> str:
    return f"{n:,}"


def fmt_rate(value: float) -> str:
    return f"{value:.2f}"


def build_markdown() -> str:
    out = [
        "# OWCS Korea 2026 Week 1 Day 1 Player Rate Stats",
        "",
        "This file aggregates the confirmed Match 1-3 player stat screenshots and computes player totals, per-minute rates, and per-10-minute rates using each player's total time played in the captured games.",
        "",
        "Rate calculation rule:",
        "- `per minute = total stat / total minutes played`",
        "- `per 10 minutes = per minute * 10`",
        "",
        "Time source:",
        "- the `Elapsed time` shown on each supplied game-data screenshot",
        "",
    ]

    for match_number in (1, 2, 3):
        match_data = parse_tables(MATCH_FILES[match_number])
        total_match_minutes = sum(game["elapsed_minutes"] for game in match_data["games"])
        aggregate = build_aggregate(match_data)

        out.extend(
            [
                f"## Match {match_number}",
                "",
                f"- Match: `{MATCH_LABELS[match_number]}`",
                f"- Games captured: `{len(match_data['games'])}`",
                f"- Total combined game time: `{total_match_minutes:.2f} minutes`",
                "",
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
            out.append(
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
        out.append("")
    return "\n".join(out)


def main() -> None:
    output = BASE / "OWCS_KOREA_2026_WEEK1_DAY1_PLAYER_RATE_STATS.md"
    output.write_text(build_markdown(), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
