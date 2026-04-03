import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
MIN_RANKING_MINUTES = 60.0

SCOPE_FILES = {
    "Week 1": [
        BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH1_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH2_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY1_MATCH3_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH1_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH2_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY2_MATCH3_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH1_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH2_STATS_REVIEW.md",
        BASE / "OWCS_KOREA_2026_WEEK1_DAY3_MATCH3_STATS_REVIEW.md",
    ],
    "Week 2": [
        BASE / "OWCS_KOREA_2026_WEEK2_DAY1_MATCH1_STATS_REVIEW.md",
    ],
}

RESULT_FILES = [
    BASE / "OWCS_KOREA_2026_WEEK1_RESULTS.md",
    BASE / "OWCS_KOREA_2026_WEEK2_RESULTS.md",
]

OUTPUT_WEEK2 = BASE / "OWCS_KOREA_2026_WEEK2_PLAYER_RATE_STATS.md"
OUTPUT_TOTAL = BASE / "OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md"
OUTPUT_TOP5 = BASE / "OWCS_KOREA_2026_CURRENT_ROLE_TOP5.md"
OUTPUT_DASHBOARD = BASE / "owcstats_current_dashboard.html"

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


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


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
                        cols = split_cells(lines[i])
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


def build_aggregate(parsed_match_data: list[dict]) -> dict:
    aggregate = defaultdict(
        lambda: {
            "team": "",
            "role": "",
            "minutes": 0.0,
            "appearances": 0,
            "E": 0,
            "A": 0,
            "D": 0,
            "DMG": 0,
            "H": 0,
            "MIT": 0,
        }
    )

    for match_data in parsed_match_data:
        for game in match_data["games"]:
            minutes = game["elapsed_minutes"]
            for team_name, players in game["teams"].items():
                for player in players:
                    row = aggregate[player["player"]]
                    row["team"] = team_name
                    row["role"] = player["role"]
                    row["minutes"] += minutes
                    row["appearances"] += 1
                    for stat in ("E", "A", "D", "DMG", "H", "MIT"):
                        row[stat] += player[stat]
    return aggregate


def rows_from_aggregate(aggregate: dict) -> list[dict]:
    rows = []
    for player in sorted(aggregate):
        row = aggregate[player]
        minutes = row["minutes"]
        if minutes <= 0:
            continue

        rows.append(
            {
                "Player": player,
                "Team": row["team"],
                "Role": row["role"],
                "Appearances": row["appearances"],
                "Minutes": minutes,
                "E": row["E"],
                "A": row["A"],
                "D": row["D"],
                "DMG": row["DMG"],
                "H": row["H"],
                "MIT": row["MIT"],
                "E/10": row["E"] / minutes * 10,
                "A/10": row["A"] / minutes * 10,
                "D/10": row["D"] / minutes * 10,
                "DMG/10": row["DMG"] / minutes * 10,
                "H/10": row["H"] / minutes * 10,
                "MIT/10": row["MIT"] / minutes * 10,
            }
        )
    return rows


def markdown_table(rows: list[dict]) -> list[str]:
    lines = [
        "| Player | Team | Role | Appearances | Minutes | E | A | D | DMG | H | MIT | E/10 | A/10 | D/10 | DMG/10 | H/10 | MIT/10 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {Player} | {Team} | {Role} | {Appearances} | {Minutes} | {E} | {A} | {D} | {DMG} | {H} | {MIT} | {E10} | {A10} | {D10} | {DMG10} | {H10} | {MIT10} |".format(
                Player=row["Player"],
                Team=row["Team"],
                Role=row["Role"],
                Appearances=fmt_num(row["Appearances"]),
                Minutes=fmt_rate(row["Minutes"]),
                E=fmt_num(row["E"]),
                A=fmt_num(row["A"]),
                D=fmt_num(row["D"]),
                DMG=fmt_num(row["DMG"]),
                H=fmt_num(row["H"]),
                MIT=fmt_num(row["MIT"]),
                E10=fmt_rate(row["E/10"]),
                A10=fmt_rate(row["A/10"]),
                D10=fmt_rate(row["D/10"]),
                DMG10=fmt_rate(row["DMG/10"]),
                H10=fmt_rate(row["H/10"]),
                MIT10=fmt_rate(row["MIT/10"]),
            )
        )
    return lines


def build_scope_markdown(title: str, rows: list[dict], parsed_match_data: list[dict]) -> str:
    total_minutes = sum(
        game["elapsed_minutes"]
        for match_data in parsed_match_data
        for game in match_data["games"]
    )
    lines = [
        f"# OWCS Korea 2026 {title} Player Rate Stats",
        "",
        f"This file aggregates the currently saved stat screenshots for {title} and computes player totals plus per-10-minute rates.",
        "",
        f"- Games captured: `{sum(len(match['games']) for match in parsed_match_data)}`",
        f"- Total combined game time: `{fmt_rate(total_minutes)} minutes`",
        "",
    ]
    lines.extend(markdown_table(rows))
    lines.append("")
    return "\n".join(lines)


def build_role_top5_markdown(rows: list[dict]) -> str:
    lines = [
        "# OWCS Korea 2026 Current Role Top 5 Rankings",
        "",
        "This file ranks the current season leaders by role using all saved screenshots so far.",
        "",
        "Ranking eligibility:",
        f"- players must have at least `{MIN_RANKING_MINUTES:.0f}` total minutes played",
        "",
    ]
    for role in ["Tank", "DPS", "Support"]:
        lines.extend([f"## {role}", ""])
        role_rows = [
            row
            for row in rows
            if row["Role"] == role and row["Minutes"] >= MIN_RANKING_MINUTES
        ]
        for metric in ["DMG/10", "H/10", "MIT/10"]:
            lines.extend(
                [
                    f"### {metric} Top 5",
                    "",
                    "| Rank | Player | Team | Minutes | Value |",
                    "| ---: | --- | --- | ---: | ---: |",
                ]
            )
            ranked = sorted(
                role_rows, key=lambda x: (-x[metric], x["Player"].lower())
            )[:5]
            for idx, row in enumerate(ranked, 1):
                lines.append(
                    f"| {idx} | {row['Player']} | {row['Team']} | {fmt_rate(row['Minutes'])} | {fmt_rate(row[metric])} |"
                )
            lines.append("")
    return "\n".join(lines)


def parse_results(files: list[Path]) -> list[dict]:
    items = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        matches = re.findall(
            r"### (\d{4}-\d{2}-\d{2}) Match (\d+)\n\n- team_1: (.+)\n- team_2: (.+)\n- winner: (.+)\n- loser: (.+)\n- series_score: (.+)\n- mvp: (.+)",
            text,
        )
        for date, match_no, team1, team2, winner, loser, score, mvp in matches:
            items.append(
                {
                    "date": date,
                    "match": int(match_no),
                    "team1": team1,
                    "team2": team2,
                    "winner": winner,
                    "loser": loser,
                    "score": score,
                    "mvp": mvp,
                }
            )
    return items


def role_top5_rows(rows: list[dict]) -> dict:
    result = {"Tank": [], "DPS": [], "Support": []}
    for role in result:
        eligible = [
            row
            for row in rows
            if row["Role"] == role and row["Minutes"] >= MIN_RANKING_MINUTES
        ]
        for metric in ["DMG/10", "H/10", "MIT/10"]:
            ranked = sorted(
                eligible, key=lambda x: (-x[metric], x["Player"].lower())
            )[:5]
            result[role].append({"metric": metric, "rows": ranked})
    return result


def build_dashboard(
    scope_rows: dict[str, list[dict]], top5_rows: dict, results: list[dict]
) -> str:
    scopes_json = json.dumps(scope_rows, ensure_ascii=False)
    top5_json = json.dumps(top5_rows, ensure_ascii=False)
    results_json = json.dumps(results, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OWCStats Current Dashboard</title>
  <style>
    :root {{
      --bg: #0a1016;
      --panel: #121b24;
      --panel2: #182331;
      --line: #223446;
      --text: #edf3fb;
      --muted: #97aabd;
      --accent: #ff6542;
      --accent2: #58d3b7;
      --gold: #f0c55a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Noto Sans KR", sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #0a0f14 0%, #0b1117 100%);
    }}
    .wrap {{
      width: min(1520px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }}
    .hero, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, .22);
    }}
    .hero {{
      padding: 28px;
      margin-bottom: 20px;
      background: linear-gradient(135deg, rgba(255,101,66,.14), rgba(88,211,183,.08));
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 42px; }}
    .hero p {{ margin: 0; color: var(--muted); }}
    .section {{ margin-top: 20px; }}
    .section-title {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }}
    .section-title h2 {{ margin: 0; font-size: 22px; }}
    .results-grid, .top5-grid {{
      display: grid;
      gap: 16px;
    }}
    .results-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .top5-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
    }}
    .result-card strong {{
      display: block;
      font-size: 18px;
      margin-bottom: 8px;
    }}
    .muted {{ color: var(--muted); font-size: 13px; }}
    .score {{
      color: var(--accent2);
      font-weight: 700;
      margin-top: 8px;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }}
    .controls input,
    .controls select {{
      background: var(--panel2);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      font-size: 14px;
    }}
    .controls input[type="text"] {{ flex: 1 1 240px; }}
    .controls input[type="number"] {{ width: 180px; }}
    .table-wrap {{
      overflow: auto;
      border-top: 1px solid var(--line);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1320px;
    }}
    th, td {{
      padding: 12px 10px;
      text-align: left;
      border-bottom: 1px solid rgba(255,255,255,.05);
      font-size: 13px;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #101821;
      color: var(--muted);
      user-select: none;
    }}
    th.sortable {{
      cursor: pointer;
    }}
    th.sortable:hover {{
      color: var(--text);
    }}
    tbody tr:hover {{
      background: rgba(255,255,255,.03);
    }}
    .rank-col {{
      width: 70px;
    }}
    .role-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
    }}
    .role-head {{
      padding: 16px 18px;
      background: linear-gradient(90deg, rgba(255,101,66,.14), rgba(88,211,183,.06));
      border-bottom: 1px solid var(--line);
    }}
    .metric-block {{
      padding: 16px 18px;
      border-top: 1px solid rgba(255,255,255,.04);
    }}
    .metric-block h4 {{
      margin: 0 0 10px;
      color: var(--gold);
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .rank-list {{
      display: grid;
      gap: 8px;
    }}
    .rank-item {{
      display: grid;
      grid-template-columns: 30px 1fr auto;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      background: var(--panel2);
      border-radius: 12px;
    }}
    .rank-num {{
      color: var(--gold);
      font-weight: 700;
    }}
    .rank-meta strong {{
      display: block;
      font-size: 14px;
    }}
    .rank-meta span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}
    .rank-value {{
      color: var(--accent2);
      font-weight: 700;
    }}
    .player-layout {{
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 16px;
    }}
    .player-list {{
      max-height: 720px;
      overflow: auto;
      padding: 12px;
      display: grid;
      gap: 10px;
    }}
    .player-button {{
      width: 100%;
      text-align: left;
      background: var(--panel2);
      color: var(--text);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 14px;
      padding: 12px 14px;
      cursor: pointer;
    }}
    .player-button.active {{
      border-color: rgba(255,101,66,.5);
      box-shadow: inset 0 0 0 1px rgba(255,101,66,.35);
    }}
    .player-button strong {{
      display: block;
      font-size: 14px;
    }}
    .player-button span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}
    .player-detail {{
      padding: 20px;
    }}
    .player-detail h3 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}
    .subline {{
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .stat-grid, .mini-grid {{
      display: grid;
      gap: 12px;
    }}
    .stat-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 18px;
    }}
    .mini-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .stat-card, .mini-card {{
      background: var(--panel2);
      border: 1px solid rgba(255,255,255,.05);
      border-radius: 14px;
      padding: 14px;
    }}
    .stat-card label, .mini-card label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .stat-card strong {{
      font-size: 24px;
    }}
    .mini-card strong {{
      font-size: 18px;
    }}
    @media (max-width: 1100px) {{
      .results-grid,
      .top5-grid,
      .player-layout,
      .stat-grid,
      .mini-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>OWCStats Current Dashboard</h1>
      <p>현재까지 정리된 OWCS Korea 2026 경기 결과와 선수 통합 지표입니다. 역할별 Top 5는 총 출전 시간 {MIN_RANKING_MINUTES:.0f}분 이상 선수만 포함합니다.</p>
    </section>

    <section class="section">
      <div class="section-title"><h2>Completed Matches</h2></div>
      <div id="resultsGrid" class="results-grid"></div>
    </section>

    <section class="section">
      <div class="section-title">
        <h2>Current Role Top 5</h2>
        <span class="muted">최소 출전 시간 {MIN_RANKING_MINUTES:.0f}분</span>
      </div>
      <div id="top5Grid" class="top5-grid"></div>
    </section>

    <section class="section panel">
      <div class="section-title" style="padding:18px 18px 0;">
        <h2>Scope Table</h2>
      </div>
      <div class="controls" style="padding:0 18px;">
        <select id="scopeSelect">
          <option value="Week 1">Week 1</option>
          <option value="Week 2">Week 2</option>
          <option value="Season Total">Season Total</option>
        </select>
        <input id="searchInput" type="text" placeholder="선수 이름 또는 팀명 검색">
        <select id="roleFilter">
          <option value="ALL">모든 역할</option>
          <option value="Tank">Tank</option>
          <option value="DPS">DPS</option>
          <option value="Support">Support</option>
        </select>
        <input id="minMinutesInput" type="number" min="0" step="1" value="0" placeholder="최소 출전 시간(분)">
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="sortable rank-col" data-sort="rank">Rank</th>
              <th class="sortable" data-sort="Team">Team</th>
              <th class="sortable" data-sort="Player">Player</th>
              <th class="sortable" data-sort="Role">Role</th>
              <th class="sortable" data-sort="E/10">E/10</th>
              <th class="sortable" data-sort="A/10">A/10</th>
              <th class="sortable" data-sort="D/10">D/10</th>
              <th class="sortable" data-sort="DMG/10">DMG/10</th>
              <th class="sortable" data-sort="H/10">H/10</th>
              <th class="sortable" data-sort="MIT/10">MIT/10</th>
              <th class="sortable" data-sort="Appearances">Appearances</th>
              <th>Appearance Time</th>
            </tr>
          </thead>
          <tbody id="overallTableBody"></tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-title"><h2>Player Detail</h2></div>
      <div class="player-layout">
        <div class="panel">
          <div class="controls" style="padding:14px 14px 0;">
            <input id="playerSearch" type="text" placeholder="선수 검색">
          </div>
          <div id="playerList" class="player-list"></div>
        </div>
        <div class="panel player-detail" id="playerDetail"></div>
      </div>
    </section>
  </div>

  <script>
    const scopeRows = {scopes_json};
    const top5Data = {top5_json};
    const results = {results_json};
    const numericFields = ["Appearances", "Minutes", "E", "A", "D", "DMG", "H", "MIT", "E/10", "A/10", "D/10", "DMG/10", "H/10", "MIT/10"];
    Object.values(scopeRows).forEach(rows => rows.forEach(row => numericFields.forEach(field => row[field] = Number(row[field]))));

    const top5Grid = document.getElementById("top5Grid");
    const resultsGrid = document.getElementById("resultsGrid");
    const overallTableBody = document.getElementById("overallTableBody");
    const searchInput = document.getElementById("searchInput");
    const roleFilter = document.getElementById("roleFilter");
    const scopeSelect = document.getElementById("scopeSelect");
    const minMinutesInput = document.getElementById("minMinutesInput");
    const playerSearch = document.getElementById("playerSearch");
    const playerList = document.getElementById("playerList");
    const playerDetail = document.getElementById("playerDetail");

    let activePlayer = null;
    let sortState = {{ key: "DMG/10", direction: "desc" }};

    function fmtNumber(value) {{
      return new Intl.NumberFormat("en-US").format(value);
    }}

    function fmtRate(value) {{
      return Number(value).toFixed(2);
    }}

    function renderResults() {{
      resultsGrid.innerHTML = "";
      results.forEach(item => {{
        const card = document.createElement("div");
        card.className = "card result-card";
        card.innerHTML = `
          <strong>${{item.date}} Match ${{item.match}}</strong>
          <div>${{item.team1}} vs ${{item.team2}}</div>
          <div class="score">${{item.winner}} ${{item.score}}</div>
          <div class="muted">MVP: ${{item.mvp}}</div>
        `;
        resultsGrid.appendChild(card);
      }});
    }}

    function renderTop5() {{
      top5Grid.innerHTML = "";
      ["Tank", "DPS", "Support"].forEach(role => {{
        const roleCard = document.createElement("div");
        roleCard.className = "role-card";
        roleCard.innerHTML = `<div class="role-head"><h3>${{role}}</h3></div>`;

        (top5Data[role] || []).forEach(group => {{
          const block = document.createElement("div");
          block.className = "metric-block";
          block.innerHTML = `<h4>${{group.metric}}</h4>`;

          const list = document.createElement("div");
          list.className = "rank-list";

          group.rows.forEach((item, index) => {{
            const row = document.createElement("div");
            row.className = "rank-item";
            row.innerHTML = `
              <div class="rank-num">#${{index + 1}}</div>
              <div class="rank-meta">
                <strong>${{item.Player}}</strong>
                <span>${{item.Team}} · ${{fmtRate(item.Minutes)}}분</span>
              </div>
              <div class="rank-value">${{fmtRate(item[group.metric])}}</div>
            `;
            list.appendChild(row);
          }});

          block.appendChild(list);
          roleCard.appendChild(block);
        }});

        top5Grid.appendChild(roleCard);
      }});
    }}

    function currentRows() {{
      return scopeRows[scopeSelect.value] || [];
    }}

    function filteredRows() {{
      const keyword = searchInput.value.trim().toLowerCase();
      const role = roleFilter.value;
      const minMinutes = Number(minMinutesInput.value || 0);

      const rows = [...currentRows()]
        .filter(row => role === "ALL" || row.Role === role)
        .filter(row => row.Minutes >= minMinutes)
        .filter(row => !keyword || row.Player.toLowerCase().includes(keyword) || row.Team.toLowerCase().includes(keyword));

      if (sortState.key === "rank") {{
        return rows;
      }}

      return rows.sort((a, b) => {{
        const key = sortState.key;
        const dir = sortState.direction === "asc" ? 1 : -1;

        if (["Team", "Player", "Role"].includes(key)) {{
          return a[key].localeCompare(b[key]) * dir;
        }}

        return ((a[key] ?? 0) - (b[key] ?? 0)) * dir;
      }});
    }}

    function renderTable() {{
      overallTableBody.innerHTML = "";

      filteredRows().forEach((row, index) => {{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${{index + 1}}</td>
          <td>${{row.Team}}</td>
          <td>${{row.Player}}</td>
          <td>${{row.Role}}</td>
          <td>${{fmtRate(row["E/10"])}}</td>
          <td>${{fmtRate(row["A/10"])}}</td>
          <td>${{fmtRate(row["D/10"])}}</td>
          <td>${{fmtRate(row["DMG/10"])}}</td>
          <td>${{fmtRate(row["H/10"])}}</td>
          <td>${{fmtRate(row["MIT/10"])}}</td>
          <td>${{fmtNumber(row["Appearances"])}}</td>
          <td>${{fmtRate(row["Minutes"])}} min</td>
        `;
        overallTableBody.appendChild(tr);
      }});
    }}

    function currentPlayerRows() {{
      const keyword = playerSearch.value.trim().toLowerCase();
      return [...currentRows()]
        .filter(row => !keyword || row.Player.toLowerCase().includes(keyword) || row.Team.toLowerCase().includes(keyword))
        .sort((a, b) => a.Player.localeCompare(b.Player));
    }}

    function renderPlayerList() {{
      const rows = currentPlayerRows();
      if (!rows.some(row => row.Player === activePlayer) && rows.length) {{
        activePlayer = rows[0].Player;
      }}

      playerList.innerHTML = "";
      rows.forEach(row => {{
        const btn = document.createElement("button");
        btn.className = "player-button" + (row.Player === activePlayer ? " active" : "");
        btn.innerHTML = `
          <strong>${{row.Player}}</strong>
          <span>${{row.Team}} · ${{row.Role}}</span>
        `;
        btn.addEventListener("click", () => {{
          activePlayer = row.Player;
          renderPlayerList();
          renderPlayerDetail();
        }});
        playerList.appendChild(btn);
      }});
    }}

    function renderPlayerDetail() {{
      const row = currentRows().find(item => item.Player === activePlayer);
      if (!row) {{
        playerDetail.innerHTML = "<p>선수를 선택해 주세요.</p>";
        return;
      }}

      playerDetail.innerHTML = `
        <h3>${{row.Player}}</h3>
        <div class="subline">${{scopeSelect.value}} · ${{row.Team}} · ${{row.Role}} · 출전 ${{row.Appearances}}회 · 총 ${{fmtRate(row.Minutes)}}분</div>
        <div class="stat-grid">
          <div class="stat-card"><label>DMG/10</label><strong>${{fmtRate(row["DMG/10"])}}</strong></div>
          <div class="stat-card"><label>H/10</label><strong>${{fmtRate(row["H/10"])}}</strong></div>
          <div class="stat-card"><label>MIT/10</label><strong>${{fmtRate(row["MIT/10"])}}</strong></div>
        </div>
        <div class="mini-grid">
          <div class="mini-card"><label>E/10</label><strong>${{fmtRate(row["E/10"])}}</strong></div>
          <div class="mini-card"><label>A/10</label><strong>${{fmtRate(row["A/10"])}}</strong></div>
          <div class="mini-card"><label>D/10</label><strong>${{fmtRate(row["D/10"])}}</strong></div>
          <div class="mini-card"><label>Total E</label><strong>${{fmtNumber(row["E"])}}</strong></div>
          <div class="mini-card"><label>Total A</label><strong>${{fmtNumber(row["A"])}}</strong></div>
          <div class="mini-card"><label>Total D</label><strong>${{fmtNumber(row["D"])}}</strong></div>
          <div class="mini-card"><label>Total DMG</label><strong>${{fmtNumber(row["DMG"])}}</strong></div>
          <div class="mini-card"><label>Total H</label><strong>${{fmtNumber(row["H"])}}</strong></div>
          <div class="mini-card"><label>Total MIT</label><strong>${{fmtNumber(row["MIT"])}}</strong></div>
        </div>
      `;
    }}

    function bindSortHeaders() {{
      document.querySelectorAll("th.sortable").forEach(th => {{
        th.addEventListener("click", () => {{
          const key = th.dataset.sort;
          if (sortState.key === key) {{
            sortState.direction = sortState.direction === "asc" ? "desc" : "asc";
          }} else {{
            sortState.key = key;
            sortState.direction = ["Team", "Player", "Role"].includes(key) ? "asc" : "desc";
          }}
          renderTable();
        }});
      }});
    }}

    searchInput.addEventListener("input", renderTable);
    roleFilter.addEventListener("change", renderTable);
    minMinutesInput.addEventListener("input", renderTable);
    playerSearch.addEventListener("input", renderPlayerList);
    scopeSelect.addEventListener("change", () => {{
      renderTable();
      renderPlayerList();
      renderPlayerDetail();
    }});

    bindSortHeaders();
    renderResults();
    renderTop5();
    renderTable();
    renderPlayerList();
    renderPlayerDetail();
  </script>
</body>
</html>
"""


def main() -> None:
    parsed_scopes = {
        scope: [parse_tables(path) for path in paths]
        for scope, paths in SCOPE_FILES.items()
    }

    scope_rows = {
        scope: rows_from_aggregate(build_aggregate(parsed))
        for scope, parsed in parsed_scopes.items()
    }

    season_matches = [match for parsed in parsed_scopes.values() for match in parsed]
    total_rows = rows_from_aggregate(build_aggregate(season_matches))
    scope_rows["Season Total"] = total_rows

    OUTPUT_WEEK2.write_text(
        build_scope_markdown("Week 2", scope_rows["Week 2"], parsed_scopes["Week 2"]),
        encoding="utf-8",
    )
    OUTPUT_TOTAL.write_text(
        build_scope_markdown("Season Total", total_rows, season_matches),
        encoding="utf-8",
    )
    OUTPUT_TOP5.write_text(
        build_role_top5_markdown(total_rows),
        encoding="utf-8",
    )
    OUTPUT_DASHBOARD.write_text(
        build_dashboard(scope_rows, role_top5_rows(total_rows), parse_results(RESULT_FILES)),
        encoding="utf-8",
    )

    print(OUTPUT_WEEK2)
    print(OUTPUT_TOTAL)
    print(OUTPUT_TOP5)
    print(OUTPUT_DASHBOARD)


if __name__ == "__main__":
    main()
