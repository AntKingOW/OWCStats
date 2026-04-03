import json
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
RATE_FILE = BASE / "OWCS_KOREA_2026_WEEK1_PLAYER_RATE_STATS.md"
TOP5_FILE = BASE / "OWCS_KOREA_2026_WEEK1_ROLE_TOP5.md"
OUTPUT_FILE = BASE / "week1_dashboard.html"
MIN_RANKING_MINUTES = 60.0


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_player_rate_file(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: dict[str, list[dict]] = {}
    current_section = None
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections[current_section] = []
            i += 1
            continue

        if current_section and line.startswith("| Player | Team | Role | Minutes |"):
            headers = split_cells(line)
            i += 2
            while i < len(lines) and lines[i].startswith("| "):
                values = split_cells(lines[i])
                if len(values) == len(headers):
                    sections[current_section].append(dict(zip(headers, values)))
                i += 1
            continue

        i += 1

    return sections


def parse_top5_file(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: dict[str, dict[str, list[dict]]] = {}
    current_role = None
    current_metric = None
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            current_role = line[3:].strip()
            result[current_role] = {}
            i += 1
            continue

        if current_role and line.startswith("### "):
            current_metric = line[4:].replace(" Top 5", "").strip()
            result[current_role][current_metric] = []
            i += 1
            continue

        if (
            current_role
            and current_metric
            and line.startswith("| Rank | Player | Team | Minutes | Value |")
        ):
            headers = split_cells(line)
            i += 2
            while i < len(lines) and lines[i].startswith("| "):
                values = split_cells(lines[i])
                if len(values) == len(headers):
                    result[current_role][current_metric].append(
                        dict(zip(headers, values))
                    )
                i += 1
            continue

        i += 1

    return result


def build_html(overall_rows: list[dict], top5: dict) -> str:
    overall_json = json.dumps(overall_rows, ensure_ascii=False)
    top5_json = json.dumps(top5, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OWCStats Week 1 Dashboard</title>
  <style>
    :root {{
      --bg: #0b1117;
      --panel: #121b24;
      --panel-2: #172330;
      --line: #243344;
      --text: #eef4fb;
      --muted: #9cb0c3;
      --accent: #ff5c39;
      --accent-2: #52d1b2;
      --gold: #f0c55a;
      --blue: #63b3ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Noto Sans KR", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255,92,57,.12), transparent 30%),
        radial-gradient(circle at top right, rgba(99,179,255,.12), transparent 28%),
        linear-gradient(180deg, #0a0f14 0%, var(--bg) 100%);
      color: var(--text);
    }}
    .wrap {{
      width: min(1400px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255,92,57,.14), rgba(82,209,178,.08));
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 24px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: 0 12px 40px rgba(0,0,0,.25);
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 5vw, 44px);
      line-height: 1.05;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }}
    .section {{
      margin-top: 20px;
    }}
    .section-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .section-title h2 {{
      margin: 0;
      font-size: 22px;
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .top5-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .role-card, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: 0 10px 28px rgba(0,0,0,.18);
    }}
    .role-head {{
      padding: 16px 18px;
      background: linear-gradient(90deg, rgba(255,92,57,.14), rgba(99,179,255,.08));
      border-bottom: 1px solid var(--line);
    }}
    .role-head h3 {{
      margin: 0;
      font-size: 18px;
    }}
    .metric-block {{
      padding: 16px 18px;
      border-top: 1px solid rgba(255,255,255,.04);
    }}
    .metric-block:first-of-type {{
      border-top: 0;
    }}
    .metric-block h4 {{
      margin: 0 0 10px;
      color: var(--gold);
      font-size: 14px;
      letter-spacing: .04em;
      text-transform: uppercase;
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
      background: var(--panel-2);
      border: 1px solid rgba(255,255,255,.04);
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
      color: var(--muted);
      font-size: 12px;
    }}
    .rank-value {{
      color: var(--accent-2);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }}
    .controls input, .controls select {{
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      font-size: 14px;
    }}
    .controls input {{
      flex: 1 1 240px;
    }}
    .table-wrap {{
      overflow: auto;
      border-top: 1px solid var(--line);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1080px;
    }}
    th, td {{
      padding: 12px 10px;
      text-align: left;
      border-bottom: 1px solid rgba(255,255,255,.05);
      font-size: 13px;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #101821;
      z-index: 1;
      color: var(--muted);
      font-weight: 600;
    }}
    tbody tr:hover {{
      background: rgba(255,255,255,.03);
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
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 14px;
      padding: 12px 14px;
      cursor: pointer;
    }}
    .player-button.active {{
      border-color: rgba(255,92,57,.5);
      box-shadow: inset 0 0 0 1px rgba(255,92,57,.35);
      background: linear-gradient(90deg, rgba(255,92,57,.16), rgba(255,92,57,.04));
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
    .stat-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .stat-card {{
      background: var(--panel-2);
      border: 1px solid rgba(255,255,255,.05);
      border-radius: 14px;
      padding: 14px;
    }}
    .stat-card label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .stat-card strong {{
      font-size: 24px;
      line-height: 1;
    }}
    .mini-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .mini-card {{
      background: rgba(255,255,255,.02);
      border: 1px solid rgba(255,255,255,.05);
      border-radius: 12px;
      padding: 12px;
    }}
    .mini-card label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .mini-card strong {{
      font-size: 18px;
    }}
    @media (max-width: 1100px) {{
      .top5-grid, .player-layout, .stat-grid, .mini-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>OWCStats Week 1 Dashboard</h1>
      <p>OWCS Korea 2026 Week 1 전체 집계와 역할별 Top 5, 선수별 상세 지표를 한 페이지에서 확인할 수 있도록 정리했습니다. 역할별 랭킹은 총 출전 시간 {MIN_RANKING_MINUTES:.0f}분 이상 선수만 포함합니다.</p>
    </section>

    <section class="section">
      <div class="section-title">
        <h2>Role Top 5</h2>
        <span style="color: var(--muted); font-size: 13px;">Minimum {MIN_RANKING_MINUTES:.0f} minutes played</span>
      </div>
      <div id="top5Grid" class="grid top5-grid"></div>
    </section>

    <section class="section panel">
      <div class="section-title" style="padding:18px 18px 0;">
        <h2>Week 1 Overall Table</h2>
      </div>
      <div class="controls" style="padding:0 18px;">
        <input id="searchInput" type="text" placeholder="선수 이름 또는 팀명 검색">
        <select id="roleFilter">
          <option value="ALL">모든 역할</option>
          <option value="Tank">Tank</option>
          <option value="DPS">DPS</option>
          <option value="Support">Support</option>
        </select>
        <select id="sortBy">
          <option value="DMG/10">DMG/10</option>
          <option value="H/10">H/10</option>
          <option value="MIT/10">MIT/10</option>
          <option value="E/10">E/10</option>
          <option value="A/10">A/10</option>
          <option value="D/10">D/10</option>
        </select>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Player</th>
              <th>Team</th>
              <th>Role</th>
              <th>Minutes</th>
              <th>E</th>
              <th>A</th>
              <th>D</th>
              <th>DMG</th>
              <th>H</th>
              <th>MIT</th>
              <th>E/10</th>
              <th>A/10</th>
              <th>D/10</th>
              <th>DMG/10</th>
              <th>H/10</th>
              <th>MIT/10</th>
            </tr>
          </thead>
          <tbody id="overallTableBody"></tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-title">
        <h2>Player Detail</h2>
      </div>
      <div class="player-layout">
        <div class="panel">
          <div class="controls" style="padding:14px 14px 0;">
            <input id="playerSearch" type="text" placeholder="선수 찾기">
          </div>
          <div id="playerList" class="player-list"></div>
        </div>
        <div class="panel player-detail" id="playerDetail"></div>
      </div>
    </section>
  </div>

  <script>
    const overallRows = {overall_json};
    const top5Data = {top5_json};

    const numericFields = ["Minutes", "E", "A", "D", "DMG", "H", "MIT", "E/10", "A/10", "D/10", "DMG/10", "H/10", "MIT/10"];
    overallRows.forEach(row => {{
      numericFields.forEach(field => row[field] = Number(String(row[field]).replaceAll(",", "")));
    }});

    const top5Grid = document.getElementById("top5Grid");
    const overallTableBody = document.getElementById("overallTableBody");
    const searchInput = document.getElementById("searchInput");
    const roleFilter = document.getElementById("roleFilter");
    const sortBy = document.getElementById("sortBy");
    const playerSearch = document.getElementById("playerSearch");
    const playerList = document.getElementById("playerList");
    const playerDetail = document.getElementById("playerDetail");

    function fmtNumber(value) {{
      return new Intl.NumberFormat("en-US").format(value);
    }}

    function fmtRate(value) {{
      return Number(value).toFixed(2);
    }}

    function renderTop5() {{
      const roleOrder = ["Tank", "DPS", "Support"];
      top5Grid.innerHTML = "";
      roleOrder.forEach(role => {{
        const roleCard = document.createElement("div");
        roleCard.className = "role-card";
        roleCard.innerHTML = `<div class="role-head"><h3>${{role}}</h3></div>`;

        ["DMG/10", "H/10", "MIT/10"].forEach(metric => {{
          const block = document.createElement("div");
          block.className = "metric-block";
          block.innerHTML = `<h4>${{metric}}</h4>`;

          const list = document.createElement("div");
          list.className = "rank-list";

          (top5Data[role]?.[metric] || []).forEach(item => {{
            const row = document.createElement("div");
            row.className = "rank-item";
            row.innerHTML = `
              <div class="rank-num">#${{item.Rank}}</div>
              <div class="rank-meta">
                <strong>${{item.Player}}</strong>
                <span>${{item.Team}} · ${{item.Minutes}}분</span>
              </div>
              <div class="rank-value">${{item.Value}}</div>
            `;
            list.appendChild(row);
          }});

          block.appendChild(list);
          roleCard.appendChild(block);
        }});

        top5Grid.appendChild(roleCard);
      }});
    }}

    function getFilteredRows() {{
      const keyword = searchInput.value.trim().toLowerCase();
      const role = roleFilter.value;
      const metric = sortBy.value;

      return [...overallRows]
        .filter(row => role === "ALL" || row.Role === role)
        .filter(row => {{
          if (!keyword) return true;
          return row.Player.toLowerCase().includes(keyword) || row.Team.toLowerCase().includes(keyword);
        }})
        .sort((a, b) => b[metric] - a[metric] || a.Player.localeCompare(b.Player));
    }}

    function renderOverallTable() {{
      const rows = getFilteredRows();
      overallTableBody.innerHTML = "";
      rows.forEach(row => {{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${{row.Player}}</td>
          <td>${{row.Team}}</td>
          <td>${{row.Role}}</td>
          <td>${{fmtRate(row["Minutes"])}}</td>
          <td>${{fmtNumber(row["E"])}}</td>
          <td>${{fmtNumber(row["A"])}}</td>
          <td>${{fmtNumber(row["D"])}}</td>
          <td>${{fmtNumber(row["DMG"])}}</td>
          <td>${{fmtNumber(row["H"])}}</td>
          <td>${{fmtNumber(row["MIT"])}}</td>
          <td>${{fmtRate(row["E/10"])}}</td>
          <td>${{fmtRate(row["A/10"])}}</td>
          <td>${{fmtRate(row["D/10"])}}</td>
          <td>${{fmtRate(row["DMG/10"])}}</td>
          <td>${{fmtRate(row["H/10"])}}</td>
          <td>${{fmtRate(row["MIT/10"])}}</td>
        `;
        overallTableBody.appendChild(tr);
      }});
    }}

    let activePlayer = overallRows.slice().sort((a, b) => a.Player.localeCompare(b.Player))[0]?.Player || null;

    function renderPlayerList() {{
      const keyword = playerSearch.value.trim().toLowerCase();
      const rows = [...overallRows]
        .filter(row => !keyword || row.Player.toLowerCase().includes(keyword) || row.Team.toLowerCase().includes(keyword))
        .sort((a, b) => a.Player.localeCompare(b.Player));

      if (!rows.some(row => row.Player === activePlayer) && rows.length) activePlayer = rows[0].Player;

      playerList.innerHTML = "";
      rows.forEach(row => {{
        const btn = document.createElement("button");
        btn.className = "player-button" + (row.Player === activePlayer ? " active" : "");
        btn.innerHTML = `<strong>${{row.Player}}</strong><span>${{row.Team}} · ${{row.Role}}</span>`;
        btn.addEventListener("click", () => {{
          activePlayer = row.Player;
          renderPlayerList();
          renderPlayerDetail();
        }});
        playerList.appendChild(btn);
      }});
    }}

    function renderPlayerDetail() {{
      const row = overallRows.find(item => item.Player === activePlayer);
      if (!row) {{
        playerDetail.innerHTML = "<p>선수를 선택해 주세요.</p>";
        return;
      }}

      playerDetail.innerHTML = `
        <h3>${{row.Player}}</h3>
        <div class="subline">${{row.Team}} · ${{row.Role}} · ${{fmtRate(row["Minutes"])}} minutes</div>

        <div class="stat-grid">
          <div class="stat-card"><label>DMG/10</label><strong>${{fmtRate(row["DMG/10"])}}</strong></div>
          <div class="stat-card"><label>H/10</label><strong>${{fmtRate(row["H/10"])}}</strong></div>
          <div class="stat-card"><label>MIT/10</label><strong>${{fmtRate(row["MIT/10"])}}</strong></div>
        </div>

        <div class="mini-grid">
          <div class="mini-card"><label>Total E</label><strong>${{fmtNumber(row["E"])}}</strong></div>
          <div class="mini-card"><label>Total A</label><strong>${{fmtNumber(row["A"])}}</strong></div>
          <div class="mini-card"><label>Total D</label><strong>${{fmtNumber(row["D"])}}</strong></div>
          <div class="mini-card"><label>Total DMG</label><strong>${{fmtNumber(row["DMG"])}}</strong></div>
          <div class="mini-card"><label>Total H</label><strong>${{fmtNumber(row["H"])}}</strong></div>
          <div class="mini-card"><label>Total MIT</label><strong>${{fmtNumber(row["MIT"])}}</strong></div>
          <div class="mini-card"><label>E/10</label><strong>${{fmtRate(row["E/10"])}}</strong></div>
          <div class="mini-card"><label>A/10</label><strong>${{fmtRate(row["A/10"])}}</strong></div>
          <div class="mini-card"><label>D/10</label><strong>${{fmtRate(row["D/10"])}}</strong></div>
        </div>
      `;
    }}

    searchInput.addEventListener("input", renderOverallTable);
    roleFilter.addEventListener("change", renderOverallTable);
    sortBy.addEventListener("change", renderOverallTable);
    playerSearch.addEventListener("input", renderPlayerList);

    renderTop5();
    renderOverallTable();
    renderPlayerList();
    renderPlayerDetail();
  </script>
</body>
</html>"""


def main() -> None:
    sections = parse_player_rate_file(RATE_FILE)
    top5 = parse_top5_file(TOP5_FILE)
    overall_rows = sections["Week 1 Overall"]
    OUTPUT_FILE.write_text(build_html(overall_rows, top5), encoding="utf-8")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
