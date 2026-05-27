#!/usr/bin/env python3
"""
Daily dashboard builder for theo-training-log.

Pulls the latest Strava activities via the Strava API, merges them into the
rolling 90-day activities.json, then renders an HTML dashboard from the template
in templates/dashboard.html.

Environment variables (set as GitHub repo secrets in CI):
    STRAVA_CLIENT_ID         The Strava app client ID
    STRAVA_CLIENT_SECRET     The Strava app client secret
    STRAVA_REFRESH_TOKEN     A long-lived refresh token for the athlete

Run locally for testing:
    export STRAVA_CLIENT_ID=...
    export STRAVA_CLIENT_SECRET=...
    export STRAVA_REFRESH_TOKEN=...
    python scripts/build_dashboard.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "activities.json"
TEMPLATE = ROOT / "templates" / "dashboard.html"
TRAINING_PLAN = ROOT / "plans" / "training-plan.md"
RACE_CALENDAR = ROOT / "knowledge" / "race-calendar.md"
INJURY_LOG = ROOT / "knowledge" / "injury-log.md"
EVOLUTION = ROOT / "knowledge" / "training-evolution.md"
LAST_SYNC = ROOT / "data" / "last-sync.txt"
DASHBOARDS_DIR = ROOT

SAST = timezone(timedelta(hours=2))
TODAY = datetime.now(SAST).date()
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
WINDOW_DAYS = 90

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def strava_refresh_access_token() -> str:
    client_id = os.environ["STRAVA_CLIENT_ID"]
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]
    refresh_token = os.environ["STRAVA_REFRESH_TOKEN"]
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(STRAVA_TOKEN_URL, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data["access_token"]


def strava_fetch_activities(access_token: str, after_ts: int) -> list[dict]:
    activities: list[dict] = []
    page = 1
    while True:
        params = urllib.parse.urlencode({"after": after_ts, "per_page": 100, "page": page})
        req = urllib.request.Request(
            f"{STRAVA_ACTIVITIES_URL}?{params}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read())
        if not batch:
            break
        activities.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return activities


SPORT_CATEGORY = {
    "Run": "run",
    "TrailRun": "run",
    "VirtualRun": "run",
    "Ride": "bike-road",
    "VirtualRide": "bike-road",
    "GravelRide": "bike-road",
    "EBikeRide": "bike-road",
    "MountainBikeRide": "bike-mtb",
    "EMountainBikeRide": "bike-mtb",
    "WeightTraining": "weights",
    "Workout": "gym-other",
    "Crossfit": "gym-other",
    "HIIT": "gym-other",
    "Pilates": "gym-other",
    "Yoga": "gym-other",
    "Hike": "walk",
    "Walk": "walk",
}


def fmt_duration(secs: int) -> str:
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_pace(secs_per_km: float) -> str:
    m, s = divmod(int(secs_per_km), 60)
    return f"{m}:{s:02d}"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def normalize_activity(a: dict) -> dict:
    start = a.get("start_date_local") or a["start_date"]
    d = datetime.fromisoformat(start.replace("Z", "+00:00"))
    distance_km = (a.get("distance") or 0) / 1000.0
    duration_sec = a.get("moving_time") or a.get("elapsed_time") or 0
    sport = a.get("type") or "Other"
    category = SPORT_CATEGORY.get(sport.replace(" ", ""), "other")
    rec: dict = {
        "id": f"{d.date().isoformat()}_{slugify(a.get('name','activity'))}_{fmt_duration(duration_sec).replace(':','-')}",
        "strava_id": a.get("id"),
        "date": d.date().isoformat(),
        "day_of_week": d.strftime("%a"),
        "sport": sport,
        "category": category,
        "title": a.get("name", ""),
        "duration_sec": int(duration_sec),
        "duration_display": fmt_duration(duration_sec),
        "distance_km": round(distance_km, 2),
        "elevation_m": int(a.get("total_elevation_gain") or 0),
        "relative_effort": int(a.get("suffer_score") or 0),
        "avg_hr": int(a.get("average_heartrate") or 0) or None,
        "max_hr": int(a.get("max_heartrate") or 0) or None,
        "synced_at": NOW_ISO,
    }
    if distance_km > 0 and duration_sec > 0:
        if category == "run" or category == "walk":
            rec["pace_per_km"] = fmt_pace(duration_sec / distance_km)
        else:
            rec["avg_speed_kmh"] = round(distance_km / (duration_sec / 3600), 1)
    return rec


def load_existing() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def merge_activities(existing: list[dict], fresh: list[dict]) -> list[dict]:
    by_id = {a["id"]: a for a in existing}
    for a in fresh:
        by_id[a["id"]] = a
    cutoff = (TODAY - timedelta(days=WINDOW_DAYS)).isoformat()
    pruned = [a for a in by_id.values() if a["date"] >= cutoff]
    pruned.sort(key=lambda a: (a["date"], a["duration_sec"]), reverse=True)
    return pruned


def parse_race_calendar(text: str) -> list[dict]:
    out: list[dict] = []
    current: dict | None = None
    in_yaml = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "```yaml":
            in_yaml = True
            continue
        if stripped == "```":
            in_yaml = False
            if current:
                out.append(current)
                current = None
            continue
        if not in_yaml:
            continue
        if stripped.startswith("- "):
            if current:
                out.append(current)
            current = {}
            kv = stripped[2:]
            if ":" in kv:
                k, v = kv.split(":", 1)
                current[k.strip()] = v.strip().strip('"').strip("'")
        elif current is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip().strip('"').strip("'")
    if current:
        out.append(current)
    return out


def parse_today_session(plan_text: str, today: date) -> tuple[str, str, str]:
    """Find the row in the plan for today's date and extract session info."""
    today_label_full = today.strftime("%d %b").lstrip("0")
    today_label_short = today.strftime("%-d %b")
    lines = plan_text.splitlines()
    for line in lines:
        if today_label_full in line or today_label_short in line:
            if "|" in line and line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 4:
                    return cells[2], cells[3], cells[0]
    return ("—", "No session scheduled today.", "")


def parse_current_week_rows(plan_text: str, today: date) -> list[dict]:
    """Find the Week table containing today and return its rows."""
    lines = plan_text.splitlines()
    week_start = today - timedelta(days=today.weekday())
    week_dates = [(week_start + timedelta(days=i)) for i in range(7)]
    week_labels = [d.strftime("%d %b").lstrip("0") for d in week_dates]
    rows = []
    for d, label in zip(week_dates, week_labels):
        match = None
        for line in lines:
            if line.startswith("|") and label in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 4:
                    match = {"day": d.strftime("%a"), "date_label": label, "planned": cells[2], "detail": cells[3]}
                    break
        if not match:
            match = {"day": d.strftime("%a"), "date_label": label, "planned": "—", "detail": ""}
        rows.append(match)
    return rows


def classify_status(planned: str, actuals: list[dict]) -> tuple[str, str, str]:
    """Returns (icon, css_class, actual_summary)."""
    if not planned or planned in {"—", "Rest"}:
        if actuals:
            return ("✅", "g", actuals[0]["title"] + " " + actuals[0]["duration_display"])
        return ("💤", "n", "—")
    planned_lower = planned.lower()
    expected = {"run": "run", "bike": "bike", "ride": "bike", "mtb": "mtb", "weights": "weight", "gym": "workout"}
    expected_category = None
    for k, v in expected.items():
        if k in planned_lower:
            expected_category = v
            break
    matched = [a for a in actuals if expected_category and expected_category in a["sport"].lower()]
    if matched:
        return ("✅", "g", matched[0]["title"] + " " + matched[0]["duration_display"])
    if actuals:
        return ("🔁", "warn", actuals[0]["title"] + " " + actuals[0]["duration_display"])
    return ("❌", "r", "—")


def race_days_to(date_str: str) -> int:
    try:
        d = date.fromisoformat(date_str)
        return (d - TODAY).days
    except Exception:
        return -1


def build_dashboard(activities: list[dict]) -> str:
    template_text = TEMPLATE.read_text()
    plan_text = TRAINING_PLAN.read_text() if TRAINING_PLAN.exists() else ""
    races_text = RACE_CALENDAR.read_text() if RACE_CALENDAR.exists() else ""
    injury_text = INJURY_LOG.read_text() if INJURY_LOG.exists() else ""
    races = parse_race_calendar(races_text)
    primary = next((r for r in races if "Imfolozi" in r.get("name", "")), None)
    secondary = next((r for r in races if "Absa" in r.get("name", "")), None)
    days_imfolozi = race_days_to(primary["date"]) if primary else "—"
    days_absa = race_days_to(secondary["date"]) if secondary else "—"

    today_actual, _, _ = parse_today_session(plan_text, TODAY)
    week_rows = parse_current_week_rows(plan_text, TODAY)
    today_session = next((r for r in week_rows if r["date_label"] == TODAY.strftime("%d %b").lstrip("0")), None)

    today_session_name = today_session["planned"] if today_session else "—"
    today_session_detail = today_session["detail"] if today_session else "Check the training plan."

    activities_by_date: dict[str, list[dict]] = {}
    for a in activities:
        activities_by_date.setdefault(a["date"], []).append(a)

    week_table_rows = []
    for r in week_rows:
        d_iso = (datetime.strptime(r["date_label"], "%d %b") if r["date_label"] else None)
        d_iso = d_iso.replace(year=TODAY.year).date().isoformat() if d_iso else ""
        actuals = activities_by_date.get(d_iso, [])
        icon, cls, actual = classify_status(r["planned"], actuals)
        week_table_rows.append(
            f'<tr><td>{r["day"]} {r["date_label"]}</td><td>{r["planned"]}</td><td>{actual}</td><td class="{cls}">{icon}</td></tr>'
        )

    seven_days_ago = (TODAY - timedelta(days=7)).isoformat()
    recent = [a for a in activities if a["date"] >= seven_days_ago]
    activity_rows = []
    for a in recent:
        sport_class = a["category"]
        pace = a.get("pace_per_km") and f'{a["pace_per_km"]}/km' or (
            a.get("avg_speed_kmh") and f'{a["avg_speed_kmh"]} km/h' or "—"
        )
        dist = f'{a["distance_km"]} km' if a["distance_km"] > 0 else "—"
        activity_rows.append(
            f'<tr><td>{a["day_of_week"]} {a["date"][8:10]}/{a["date"][5:7]}</td>'
            f'<td><span class="sport {sport_class}">{a["sport"]}</span></td>'
            f'<td>{a["title"]}</td>'
            f'<td class="m">{a["duration_display"]}</td>'
            f'<td class="m">{dist}</td>'
            f'<td class="m">{pace}</td>'
            f'<td class="m">{a["relative_effort"]}</td></tr>'
        )

    race_cards = []
    for r in races:
        days = race_days_to(r.get("date", ""))
        pri = (r.get("priority") or "").upper()
        css_priority = f'priority-{pri.lower()}' if pri in ("A", "B", "C") else "priority-c"
        pri_label = "A · Peak" if pri == "A" else ("B · Real Race" if pri == "B" else "Season")
        countdown_color = "var(--primary)" if pri == "A" else "var(--accent)" if pri == "B" else "var(--t2)"
        race_cards.append(
            f'<div class="race-card {css_priority}">'
            f'<div class="race-priority {pri.lower()}">{pri_label}</div>'
            f'<div class="race-name">{r.get("name","")}</div>'
            f'<div class="race-countdown" style="color:{countdown_color}">{days}d</div>'
            f'<div class="race-date">{r.get("date","")} · {r.get("location","")}</div>'
            f'<div class="race-target">Target: {r.get("target","")}</div>'
            f'<div style="font-size:.68rem;color:var(--t2);margin-top:8px;line-height:1.5">{r.get("notes","")}</div>'
            f'</div>'
        )

    weekly_runs = sum(a["distance_km"] for a in activities if a["category"] == "run" and a["date"] >= (TODAY - timedelta(days=28)).isoformat())
    weekly_bike = sum(
        a["distance_km"]
        for a in activities
        if a["category"] in ("bike-road", "bike-mtb") and a["date"] >= (TODAY - timedelta(days=28)).isoformat()
    )
    week_hours = sum(a["duration_sec"] for a in activities if a["date"] >= (TODAY - timedelta(days=today.weekday() if (today := TODAY) else 0)).isoformat()) / 3600

    substitutions = {
        "{{DATE}}": TODAY.strftime("%a %d %b %Y"),
        "{{ASOF}}": NOW_ISO,
        "{{CYCLE_N}}": str(count_cycles()),
        "{{WEEK_LABEL}}": detect_week_label(plan_text, TODAY),
        "{{DAYS_TO_IMFOLOZI}}": str(days_imfolozi),
        "{{DAYS_TO_ABSA}}": str(days_absa),
        "{{TODAY_SESSION_NAME}}": today_session_name,
        "{{TODAY_SESSION_DETAIL}}": today_session_detail,
        "{{TODAY_SESSION_DURATION}}": "see plan",
        "{{TODAY_SESSION_INTENSITY}}": "see plan",
        "{{WEEK_TABLE_ROWS}}": "\n".join(week_table_rows),
        "{{ACTIVITY_TABLE_ROWS}}": "\n".join(activity_rows) if activity_rows else '<tr><td colspan="7" style="text-align:center;color:var(--t3)">No activities in the last 7 days</td></tr>',
        "{{RACE_CARDS}}": "\n".join(race_cards),
        "{{WEEK_HOURS}}": f"{week_hours:.1f}h",
        "{{WEEK_KM}}": "—",
        "{{ADHERENCE_PCT}}": "—",
        "{{ADHERENCE_FRAC}}": "—",
        "{{RUN_KM_4WK}}": f"{weekly_runs:.1f}",
        "{{RUN_KM_TREND}}": "",
        "{{BIKE_KM_4WK}}": f"{weekly_bike:.1f}",
        "{{BIKE_KM_TREND}}": "",
        "{{FOOT_STATUS}}": "90%",
        "{{FOOT_LAST}}": parse_injury_last(injury_text),
        "{{INJURY_BANNER}}": render_injury_banner(injury_text),
        "{{NEXT_4_WEEKS_TABLE}}": '<tr><td colspan="5" style="text-align:center;color:var(--t3)">See training plan</td></tr>',
        "{{CALENDAR_GRID}}": render_calendar_grid(activities),
        "{{EVOLUTION_NOTE}}": latest_evolution_note(),
        "{{CHARTS_SCRIPT}}": render_charts_script(activities),
    }

    out = template_text
    for k, v in substitutions.items():
        out = out.replace(k, str(v))
    return out


def count_cycles() -> int:
    if not EVOLUTION.exists():
        return 1
    txt = EVOLUTION.read_text()
    return len(re.findall(r"^## Cycle ", txt, re.MULTILINE)) + 1


def detect_week_label(plan_text: str, today: date) -> str:
    matches = re.findall(r"## Week (\d+) \((\d+)[–-](\d+) (\w+)\)\s+—\s+(.+)", plan_text)
    today_day = today.day
    today_month = today.strftime("%b")
    for w, start, end, mon, label in matches:
        if mon == today_month and int(start) <= today_day <= int(end):
            return f"Week {w} — {label}"
    return f"Week — {today.strftime('%d %b')}"


def parse_injury_last(text: str) -> str:
    if not text:
        return "—"
    m = re.search(r"\*\*Current status:\*\*\s*([^\n]+)", text)
    return m.group(1)[:80] if m else "—"


def render_injury_banner(text: str) -> str:
    status_line = parse_injury_last(text)
    return f'''<div class="injury-banner">
  <div>
    <div class="t">Foot Status — Right Plantar Fasciitis</div>
    <div class="c">{status_line}</div>
    <div class="sub">Continue daily prehab. See PF protocol in plans/.</div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;color:var(--green);font-weight:700">0/10</div>
</div>'''


def latest_evolution_note() -> str:
    if not EVOLUTION.exists():
        return "First cycle bootstrap."
    txt = EVOLUTION.read_text()
    cycles = re.split(r"^## Cycle ", txt, flags=re.MULTILINE)
    if len(cycles) < 2:
        return "First cycle bootstrap."
    last = cycles[-1]
    obs = re.search(r"Observations?:\s*([^\n]+)", last)
    if obs:
        return obs.group(1)
    return last[:300].replace("\n", " ").strip()


def render_calendar_grid(activities: list[dict]) -> str:
    cells = []
    start = TODAY - timedelta(days=30)
    start = start - timedelta(days=start.weekday())
    days = [start + timedelta(days=i) for i in range(91)]
    by_date = {}
    for a in activities:
        by_date.setdefault(a["date"], []).append(a)
    for d in days:
        d_iso = d.isoformat()
        klass = ""
        symbol = ""
        if d == TODAY:
            klass = "today"
        elif d < TODAY:
            if d_iso in by_date:
                klass = "past-done"
                symbol = by_date[d_iso][0]["category"][:3]
            else:
                klass = "past-rest"
        else:
            klass = ""
        cells.append(f'<div class="cal-cell {klass}"><div class="d">{d.day}</div><div class="s">{symbol or "—"}</div></div>')
    return "\n".join(cells)


def render_charts_script(activities: list[dict]) -> str:
    return """
const commonOpts={responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8',font:{size:10}}},y:{ticks:{color:'#94a3b8',font:{size:10}},beginAtZero:true}}};
const _empty = (id) => new Chart(document.getElementById(id),{type:'bar',data:{labels:[],datasets:[]},options:commonOpts});
_empty('chartVolume'); _empty('chartRunKm'); _empty('chartBikeKm'); _empty('chartLongest');
// TODO: render real per-week aggregates here from the embedded activities.json
"""


def append_evolution_entry(activities: list[dict]) -> None:
    """Append a new dated entry to the evolution journal."""
    last_7 = [a for a in activities if a["date"] >= (TODAY - timedelta(days=7)).isoformat()]
    summary = f"{len(last_7)} activities in last 7 days, {len(activities)} in 90-day window."
    entry = f"""

---

## Cycle {count_cycles()} — {TODAY.isoformat()} (auto-generated)

- **Sync at:** {NOW_ISO}
- **Activity baseline:** {summary}
- **Today's planned session:** parsed from plan
- **Notes:** Auto-cycle. Patterns and observations to be added by manual review or by next /my-training session.
"""
    if EVOLUTION.exists():
        EVOLUTION.write_text(EVOLUTION.read_text() + entry)


def write_outputs(html: str, activities: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(activities, indent=2))
    dashboard_path = DASHBOARDS_DIR / f"training-dashboard-{TODAY.isoformat()}.html"
    dashboard_path.write_text(html)
    (DASHBOARDS_DIR / "index.html").write_text(html)
    LAST_SYNC.write_text(f"OK {NOW_ISO}\nsource: Strava API\nactivities_synced: {len(activities)}\n")


def main() -> int:
    print(f"my-training build · {NOW_ISO}", file=sys.stderr)
    try:
        token = strava_refresh_access_token()
        print("✓ Strava token refreshed", file=sys.stderr)
    except Exception as e:
        print(f"✗ Strava token refresh failed: {e}", file=sys.stderr)
        return 2
    after_ts = int((datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).timestamp())
    try:
        raw = strava_fetch_activities(token, after_ts)
        print(f"✓ Strava activities fetched: {len(raw)}", file=sys.stderr)
    except Exception as e:
        print(f"✗ Strava fetch failed: {e}", file=sys.stderr)
        return 3
    fresh = [normalize_activity(a) for a in raw]
    existing = load_existing()
    merged = merge_activities(existing, fresh)
    print(f"✓ Merged: {len(merged)} activities in {WINDOW_DAYS}-day window", file=sys.stderr)
    html = build_dashboard(merged)
    write_outputs(html, merged)
    append_evolution_entry(merged)
    print(f"✓ Dashboard written: training-dashboard-{TODAY.isoformat()}.html", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
