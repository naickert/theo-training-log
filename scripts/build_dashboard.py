#!/usr/bin/env python3
"""
Daily dashboard builder for theo-training-log.

Pulls the latest Strava activities via the Strava API, merges them into the
rolling 90-day activities.json, then renders the editorial HTML dashboard
from templates/dashboard.html.

Environment variables (set as GitHub repo secrets in CI):
    STRAVA_CLIENT_ID
    STRAVA_CLIENT_SECRET
    STRAVA_REFRESH_TOKEN
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
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


# ---------- STRAVA ----------

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


# ---------- ACTIVITY NORMALIZATION ----------

SPORT_CATEGORY = {
    "Run": "run", "TrailRun": "run", "VirtualRun": "run",
    "Ride": "bike", "VirtualRide": "bike", "GravelRide": "bike", "EBikeRide": "bike",
    "MountainBikeRide": "mtb", "EMountainBikeRide": "mtb",
    "WeightTraining": "weights",
    "Workout": "other", "Crossfit": "other", "HIIT": "other", "Pilates": "other", "Yoga": "other",
    "Hike": "walk", "Walk": "walk",
}
CATEGORY_LABEL = {"run": "Run", "bike": "Bike", "mtb": "MTB", "weights": "Weights", "other": "Gym", "walk": "Walk"}


def fmt_duration(secs: int) -> str:
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_short_duration(secs: int) -> str:
    h, rem = divmod(int(secs), 3600)
    m, _ = divmod(rem, 60)
    return f"{h}:{m:02d}" if h else f"{m} min"


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
    sport = (a.get("type") or "Other").replace(" ", "")
    category = SPORT_CATEGORY.get(sport, "other")
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
        elif category in ("bike", "mtb"):
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


# ---------- PLAN / RACE PARSING ----------

def parse_race_calendar(text: str) -> list[dict]:
    out: list[dict] = []
    current: dict | None = None
    in_yaml = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "```yaml":
            in_yaml = True; continue
        if stripped == "```":
            in_yaml = False
            if current: out.append(current); current = None
            continue
        if not in_yaml:
            continue
        if stripped.startswith("- "):
            if current: out.append(current)
            current = {}
            kv = stripped[2:]
            if ":" in kv:
                k, v = kv.split(":", 1)
                current[k.strip()] = v.strip().strip('"').strip("'")
        elif current is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip().strip('"').strip("'")
    if current: out.append(current)
    return out


def detect_week_block(plan_text: str, today: date) -> tuple[int, str, str, list[dict]]:
    """Return (week_n, label, date_range, rows). Each row: {day, date_iso, planned, detail}."""
    # Find current week by scanning week headers like "## Week 10 (25–31 May) — Re-base"
    header_re = re.compile(r"^##\s+Week\s+(\d+)\s*\((\d+)[–-](\d+)\s+(\w+)(?:\s*[–-]\s*\d+\s+(\w+))?\)\s*—\s*(.+)$", re.MULTILINE)
    matches = list(header_re.finditer(plan_text))
    months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    current_match = None
    for m in matches:
        wn = int(m.group(1))
        start_day = int(m.group(2))
        end_day = int(m.group(3))
        month1 = months.get(m.group(4), 0)
        month2 = months.get(m.group(5) or m.group(4), month1)
        if not month1: continue
        try:
            start_d = date(today.year, month1, start_day)
            end_d = date(today.year, month2, end_day)
        except ValueError:
            continue
        if start_d <= today <= end_d:
            current_match = m
            label = m.group(6).strip()
            week_n = wn
            date_range = f"{start_day}–{end_day} {m.group(4)}"
            break
    if not current_match:
        return (0, "—", "", [])

    # Extract this week's table rows
    next_match_start = matches[matches.index(current_match)+1].start() if matches.index(current_match)+1 < len(matches) else len(plan_text)
    section = plan_text[current_match.end():next_match_start]
    rows = []
    week_start = today - timedelta(days=today.weekday())
    for i in range(7):
        d = week_start + timedelta(days=i)
        day_short = d.strftime("%a")
        day_num = d.day
        month_short = d.strftime("%b")
        # Look for a row matching the day number + month
        row_re = re.compile(rf"^\|\s*{day_short}\s*\|\s*{day_num}\s+{month_short}\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", re.MULTILINE)
        m = row_re.search(section)
        if m:
            rows.append({"day": day_short, "date": d.isoformat(), "date_label": f"{day_num} {month_short}",
                        "planned": m.group(1).strip(), "detail": m.group(2).strip()})
        else:
            rows.append({"day": day_short, "date": d.isoformat(), "date_label": f"{day_num} {month_short}",
                        "planned": "—", "detail": ""})
    return (week_n, label, date_range, rows)


# ---------- WORD HELPERS ----------

UNITS_WORDS = ["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
TENS_WORDS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def n_to_word(n: int) -> str:
    if n < 20: return UNITS_WORDS[n]
    if n < 100:
        t, u = divmod(n, 10)
        return TENS_WORDS[t] + ("-" + UNITS_WORDS[u] if u else "")
    return str(n)


def n_to_ordinal_word(n: int) -> str:
    ord_special = {1:"first",2:"second",3:"third",5:"fifth",8:"eighth",9:"ninth",12:"twelfth",20:"twentieth",30:"thirtieth"}
    if n in ord_special: return ord_special[n]
    if n < 20:
        return UNITS_WORDS[n] + "th"
    if n % 10 == 0:
        return TENS_WORDS[n//10][:-1] + "ieth"
    t, u = divmod(n, 10)
    base_u = ord_special.get(u, UNITS_WORDS[u] + "th")
    return TENS_WORDS[t] + "-" + base_u


def to_roman(n: int) -> str:
    if n <= 0: return "0"
    vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    out = ""
    for v, sym in vals:
        while n >= v:
            out += sym; n -= v
    return out


def long_date_words(d: date) -> str:
    day_words = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    yr = d.year
    century = yr // 100
    last_two = yr % 100
    if century == 20:
        year_words = f"twenty {n_to_word(last_two).replace('-',' ')}"
    else:
        year_words = str(yr)
    return f"{day_words[d.weekday()]} the {n_to_ordinal_word(d.day)} of {MONTHS[d.month-1]}, {year_words}"


def race_days_to(date_str: str) -> int:
    try:
        d = date.fromisoformat(date_str)
        return (d - TODAY).days
    except Exception:
        return -1


def long_race_date(date_str: str) -> str:
    try:
        d = date.fromisoformat(date_str)
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        return f"{day_names[d.weekday()]} {d.day} {MONTHS[d.month-1]} {d.year}"
    except Exception:
        return date_str


# ---------- HTML RENDERERS ----------

def _esc(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def render_stat(label: str, val: str, unit: str, sub: str, cls: str = "") -> str:
    return (
        f'<div class="stat">'
        f'<span class="stat-label">{_esc(label)}</span>'
        f'<div class="stat-value {cls}">{_esc(val)}<small>{_esc(unit)}</small></div>'
        f'<div class="stat-sub">{_esc(sub)}</div>'
        f'</div>'
    )


def render_stats(activities: list[dict], week_rows: list[dict]) -> str:
    # this-week hours
    week_start = TODAY - timedelta(days=TODAY.weekday())
    week_acts = [a for a in activities if a["date"] >= week_start.isoformat() and a["date"] <= TODAY.isoformat()]
    week_hours = sum(a["duration_sec"] for a in week_acts) / 3600
    week_done = sum(1 for r in week_rows if date.fromisoformat(r["date"]) <= TODAY and r["planned"] not in ("—","Rest"))
    # 4 week buckets
    cutoff_4w = (TODAY - timedelta(days=28)).isoformat()
    acts_4w = [a for a in activities if a["date"] >= cutoff_4w]
    run_4w = sum(a["distance_km"] for a in acts_4w if a["category"] == "run")
    bike_4w = sum(a["distance_km"] for a in acts_4w if a["category"] in ("bike","mtb"))
    longest = max((a for a in activities if a["category"] in ("bike","mtb") and a["distance_km"] > 0),
                  key=lambda x: x["distance_km"], default=None)
    longest_km = longest["distance_km"] if longest else 0
    longest_ago = (TODAY - date.fromisoformat(longest["date"])).days if longest else 0

    return "".join([
        render_stat("This Week", f"{week_hours:.1f}", "h", f"{week_done} of 7 days complete"),
        render_stat("4-Wk Run", f"{run_4w:.0f}", "km", "post-PF rebuild phase"),
        render_stat("4-Wk Bike", f"{bike_4w:.0f}", "km", "ramp begins this week", cls="alert" if bike_4w < 80 else ""),
        render_stat("Longest Ride", f"{longest_km:.0f}", "km", f"{longest_ago} days ago · iMfolozi needs 50+"),
        render_stat("Foot", "90", "%", "resolving · 0/10 pain", cls="good"),
    ])


def render_today(week_rows: list[dict]) -> tuple[str, str, str, str, str, str]:
    """Returns (tag, title_html, detail_html, meta_html, sec_meta, observation)."""
    today_row = next((r for r in week_rows if r["date"] == TODAY.isoformat()), None)
    if not today_row or today_row["planned"] in ("—",):
        return ("Rest day", "<em>Rest</em>", "No session prescribed.", "", "", "Recovery is training. Hydrate and sleep.")

    planned = today_row["planned"]
    detail = today_row["detail"]
    # Strip ~~strike~~ markers
    planned_clean = re.sub(r"~~(.+?)~~", r"\1", planned)
    detail_clean = re.sub(r"~~(.+?)~~", r"\1", detail)
    # Render bold/italic markdown
    planned_clean = re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", planned_clean)
    detail_clean = re.sub(r"\*\*(.+?)\*\*", r"<span class='accent'>\1</span>", detail_clean)

    tag = f"{TODAY.strftime('%A')} · current week"
    title_html = planned_clean if "<em>" in planned_clean else f"<em>{planned_clean}</em>"
    detail_html = detail_clean

    # Extract structured meta: look for HR ranges, durations
    meta_items = []
    duration_m = re.search(r"~?\s*(\d+)\s*min", detail)
    if duration_m: meta_items.append(("Duration", f"~{duration_m.group(1)} min"))
    hr_m = re.search(r"HR\s*(\d+[\s\-–]+\d+)", detail)
    if hr_m: meta_items.append(("HR Target", hr_m.group(1).replace(" ","").replace("-","–")))
    rpe_m = re.search(r"RPE\s*(\d+(?:\s*[–-]\s*\d+)?)", detail)
    if rpe_m: meta_items.append(("RPE", rpe_m.group(1)))
    mode_hints = {"bike":"Bike","mtb":"MTB","run":"Run","weights":"Weights","gym":"Gym"}
    mode = next((label for k,label in mode_hints.items() if k in planned.lower()), "Mixed")
    meta_items.append(("Mode", mode))

    meta_html = "".join(f'<div class="today-meta-item">{k}<strong>{_esc(v)}</strong></div>' for k,v in meta_items)
    sec_meta = f"Day {to_roman(TODAY.weekday()+1)}"

    observation = "Today's planned session — follow the structure, respect the heart-rate ceiling, and don't extend on a whim."
    return (tag, title_html, detail_html, meta_html, sec_meta, observation)


def render_injury_banner(text: str) -> str:
    status_line = "Resolving — ~90% recovered. Daily prehab continues."
    score = "0"
    sub = "morning pain"
    if text:
        m = re.search(r"\*\*Current status:\*\*\s*([^\n]+)", text)
        if m: status_line = m.group(1)
    return f'''<div class="margin-note">
  <div class="margin-note-body">
    <div class="margin-note-label">Foot · Right Plantar Fasciitis</div>
    {_esc(status_line)} Continue daily prehab: plantar fascia stretch, frozen-bottle roll, calf stretches, eccentric heel drops.
  </div>
  <div>
    <div class="margin-note-score">{score}<span style="font-size:22px;color:var(--forest-2)">/10</span></div>
    <div class="margin-note-score-sub">{sub}</div>
  </div>
</div>'''


def render_week_rows(week_rows: list[dict], activities_by_date: dict) -> str:
    out = []
    for r in week_rows:
        d_iso = r["date"]
        d_obj = date.fromisoformat(d_iso)
        day_short = r["day"]
        day_num = d_obj.day
        planned = r["planned"]
        detail = r["detail"]
        is_today = (d_obj == TODAY)
        # Strip strike formatting
        planned_clean = re.sub(r"~~(.+?)~~", r'<span class="strike">\1</span>', planned)
        planned_clean = re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", planned_clean)
        # Combine planned + brief detail
        session_html = planned_clean
        if detail and detail != "Done" and not detail.startswith("done") and len(detail) < 120:
            session_html += " — " + re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", detail)
        elif detail and len(detail) >= 120:
            session_html += " — " + re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", detail[:110]) + "…"

        # Status
        actuals = activities_by_date.get(d_iso, [])
        if d_obj < TODAY:
            if planned.lower().startswith("~~") or "done" in detail.lower():
                status, status_cls = "Complete", "done"
            elif "rest" in planned.lower():
                status, status_cls = "rest", "rest"
            elif actuals:
                status, status_cls = "Complete", "done"
            else:
                status, status_cls = "Missed", "rest"
        elif d_obj == TODAY:
            status, status_cls = "Today", "today-mark"
        else:
            if "rest" in planned.lower():
                status, status_cls = "rest", "rest"
            else:
                status, status_cls = "Upcoming", "upcoming"

        row_cls = " today-row" if is_today else ""
        day_cls = " today-mark" if is_today else ""
        out.append(
            f'<div class="week-row{row_cls}">'
            f'<div class="week-day{day_cls}">{day_short}<strong>{day_num}</strong></div>'
            f'<div class="week-session">{session_html}</div>'
            f'<div class="week-status {status_cls}">{status}</div>'
            f'</div>'
        )
    return "".join(out)


def render_log_entries(activities: list[dict]) -> str:
    seven_days_ago = (TODAY - timedelta(days=7)).isoformat()
    recent = [a for a in activities if a["date"] >= seven_days_ago]
    # Dedupe by id (handle the duplicates that come from manual scrape + API merge)
    seen = set()
    deduped = []
    for a in recent:
        key = (a["date"], a["title"], a["duration_sec"])
        if key in seen: continue
        seen.add(key)
        deduped.append(a)
    out = []
    for a in deduped[:8]:
        d_obj = date.fromisoformat(a["date"])
        day = a["day_of_week"]
        num = d_obj.day
        cat = a["category"]
        sport_label = CATEGORY_LABEL.get(cat, "Other")
        title = a["title"]
        meta_bits = []
        if a.get("pace_per_km"):
            meta_bits.append(f"Pace {a['pace_per_km']}/km")
        elif a.get("avg_speed_kmh"):
            meta_bits.append(f"Avg {a['avg_speed_kmh']} km/h")
        if a.get("relative_effort"):
            meta_bits.append(f"RE {a['relative_effort']}")
        meta = " · ".join(meta_bits) if meta_bits else "—"

        if a["distance_km"] > 0:
            stats_main = f'{a["distance_km"]:.2f}'
            stats_sub = f"km · {a['duration_display']}"
        else:
            stats_main = a["duration_display"]
            stats_sub = "duration"

        out.append(
            f'<div class="log-entry">'
            f'<div class="log-date"><span class="day">{day}</span><span class="num">{num}</span></div>'
            f'<div>'
            f'<div class="log-title"><span class="log-sport {cat}">{sport_label}</span>{_esc(title)}</div>'
            f'<div class="log-meta">{_esc(meta)}</div>'
            f'</div>'
            f'<div class="log-stats">{stats_main} <span class="sub">{stats_sub}</span></div>'
            f'</div>'
        )
    return "".join(out) if out else '<div class="log-entry"><div></div><div>No activities in the last 7 days.</div><div></div></div>'


def render_races(races: list[dict]) -> str:
    out = []
    for i, r in enumerate(races):
        days = race_days_to(r.get("date",""))
        pri = (r.get("priority") or "").upper()
        cls_map = {"A": "", "B": "b-race", "C": "c-race"}
        cls = cls_map.get(pri, "c-race")
        # First A-race shown first as primary; subsequent A-races demoted visually
        if pri == "A" and i > 0:
            cls = "c-race"

        priority_label_map = {"A": "A-Race · Peak Event", "B": "B-Race · Road", "C": "Season Goal"}
        priority_label = priority_label_map.get(pri, "Season")
        if pri == "A" and i > 0: priority_label = "Season Goal"

        name = r.get("name", "")
        # Try to find an italic-emphasizable token
        name_html = re.sub(r"^(\w+)", r"<em>\1</em>", name) if " " in name else f"<em>{name}</em>"
        long_dt = long_race_date(r.get("date",""))
        location = r.get("location","")
        date_line = f"{long_dt}{(' · ' + location) if location else ''}"
        target_line = r.get("target", "")
        notes = r.get("notes", "")

        days_str = str(days) if days >= 0 else "—"
        out.append(
            f'<article class="race-feature {cls}">'
            f'<div class="race-count {cls}">{days_str}<small>days</small></div>'
            f'<div>'
            f'<div class="race-priority">{_esc(priority_label)}</div>'
            f'<h3 class="race-name">{name_html}</h3>'
            f'<div class="race-date">{_esc(date_line)}</div>'
            f'<p class="race-target"><strong>Target: {_esc(target_line)}</strong> {_esc(notes)}</p>'
            f'</div>'
            f'</article>'
        )
    return "".join(out)


def compute_weekly_buckets(activities: list[dict], n_weeks: int = 12) -> dict:
    """Returns dict of week_start_iso -> {hours, runKm, bikeKm, longestMin}."""
    weeks = defaultdict(lambda: {"hours": 0.0, "runKm": 0.0, "bikeKm": 0.0, "longestMin": 0.0})
    seen = set()
    for a in activities:
        # Dedup
        key = (a["date"], a["title"], a["duration_sec"])
        if key in seen: continue
        seen.add(key)
        d = date.fromisoformat(a["date"])
        ws = (d - timedelta(days=d.weekday())).isoformat()
        weeks[ws]["hours"] += a["duration_sec"] / 3600
        if a["category"] == "run":
            weeks[ws]["runKm"] += a["distance_km"]
        elif a["category"] in ("bike", "mtb"):
            weeks[ws]["bikeKm"] += a["distance_km"]
        weeks[ws]["longestMin"] = max(weeks[ws]["longestMin"], a["duration_sec"] / 60)
    # Fill the last n_weeks
    today_week_start = TODAY - timedelta(days=TODAY.weekday())
    series = []
    for i in range(n_weeks - 1, -1, -1):
        ws = (today_week_start - timedelta(weeks=i)).isoformat()
        b = weeks.get(ws, {"hours":0,"runKm":0,"bikeKm":0,"longestMin":0})
        series.append({"week": ws, **b})
    return series


def render_trends(weekly: list[dict]) -> str:
    latest = weekly[-1] if weekly else {"hours":0,"runKm":0,"bikeKm":0,"longestMin":0}
    prev = weekly[-2] if len(weekly) > 1 else latest
    def delta_class(now, then):
        if now > then * 1.1: return "good"
        if now < then * 0.9: return "warn"
        return ""
    def delta_text(now, then, unit, label):
        if then == 0:
            return f"{label} this week"
        direction = "↑" if now > then else "↓"
        return f"{direction} from {then:.1f}{unit} prior week"

    hours_chart = [round(w["hours"],1) for w in weekly]
    run_chart = [round(w["runKm"],1) for w in weekly]
    bike_chart = [round(w["bikeKm"],1) for w in weekly]
    longest_chart = [int(w["longestMin"]) for w in weekly]

    return (
        f'<div>'
        f'<div class="trend-label">Weekly Hours</div>'
        f'<div class="trend-value">{latest["hours"]:.1f}<small>h</small></div>'
        f'<div class="trend-delta {delta_class(latest["hours"],prev["hours"])}">{delta_text(latest["hours"],prev["hours"],"h","first session")}</div>'
        f'<div class="trend-chart"><canvas id="chartHours"></canvas></div>'
        f'</div>'
        f'<div>'
        f'<div class="trend-label">Running Kilometres</div>'
        f'<div class="trend-value">{latest["runKm"]:.1f}<small>km</small></div>'
        f'<div class="trend-delta {delta_class(latest["runKm"],prev["runKm"])}">{delta_text(latest["runKm"],prev["runKm"]," km","building")}</div>'
        f'<div class="trend-chart"><canvas id="chartRun"></canvas></div>'
        f'</div>'
        f'<div>'
        f'<div class="trend-label">Bike Kilometres</div>'
        f'<div class="trend-value" style="color:var(--ember)">{latest["bikeKm"]:.1f}<small>km</small></div>'
        f'<div class="trend-delta {delta_class(latest["bikeKm"],prev["bikeKm"])}">{delta_text(latest["bikeKm"],prev["bikeKm"]," km","ramping")}</div>'
        f'<div class="trend-chart"><canvas id="chartBike"></canvas></div>'
        f'</div>'
        f'<div>'
        f'<div class="trend-label">Longest Session</div>'
        f'<div class="trend-value">{int(latest["longestMin"])}<small>min</small></div>'
        f'<div class="trend-delta {delta_class(latest["longestMin"],prev["longestMin"])}">need 3 hr+ rides soon</div>'
        f'<div class="trend-chart"><canvas id="chartLongest"></canvas></div>'
        f'</div>'
    ), {"hours": hours_chart, "runKm": run_chart, "bikeKm": bike_chart, "longestMin": longest_chart}


def build_calendar_data(activities: list[dict], races: list[dict]) -> dict:
    acts = {}
    seen = set()
    for a in activities:
        key = (a["date"], a["title"], a["duration_sec"])
        if key in seen: continue
        seen.add(key)
        label = {"run":"R","bike":"B","mtb":"MTB","weights":"W","other":"G","walk":"W"}.get(a["category"], "·")
        acts[a["date"]] = label

    race_cells = []
    for i, r in enumerate(races):
        date_str = r.get("date", "")
        pri = (r.get("priority") or "").upper()
        if pri == "A" and i == 0:
            race_cells.append({"date": date_str, "cls": "race", "mark": "RACE"})
        elif pri == "B":
            race_cells.append({"date": date_str, "cls": "race-b", "mark": "B-Race"})

    return {
        "today": TODAY.isoformat(),
        "activities": acts,
        "planned": {},  # TODO: parse future planned sessions from the training plan
        "races": race_cells,
    }


# ---------- TEMPLATE SUBSTITUTION ----------

def build_dashboard(activities: list[dict]) -> str:
    template_text = TEMPLATE.read_text()
    plan_text = TRAINING_PLAN.read_text() if TRAINING_PLAN.exists() else ""
    races_text = RACE_CALENDAR.read_text() if RACE_CALENDAR.exists() else ""
    injury_text = INJURY_LOG.read_text() if INJURY_LOG.exists() else ""

    races = parse_race_calendar(races_text)
    primary = next((r for r in races if (r.get("priority","").upper() == "A" and "Imfolozi" in r.get("name",""))), races[0] if races else None)
    if primary is None:
        primary = {"name": "(no race)", "date": "", "distance_km": "", "type": "", "target": ""}

    days_primary = race_days_to(primary.get("date",""))
    week_n, week_label, week_range, week_rows = detect_week_block(plan_text, TODAY)

    activities_by_date = defaultdict(list)
    for a in activities:
        activities_by_date[a["date"]].append(a)

    today_tag, today_title_html, today_detail_html, today_meta_html, today_sec_meta, today_observation = render_today(week_rows)

    weekly = compute_weekly_buckets(activities, 12)
    trends_html, chart_data = render_trends(weekly)
    calendar_data = build_calendar_data(activities, races)

    # Short race label
    race_name = primary.get("name", "")
    hero_race_short = "iMfolozi" if "Imfolozi" in race_name else race_name.split()[0]
    hero_kicker = f"A-Race · {primary.get('type','')} · Peak Event".strip(" ·")
    distance_km = primary.get("distance_km", "")
    hero_details = f"{distance_km} kilometres <span class='sep'>·</span> {primary.get('type','race').lower()} <span class='sep'>·</span> {long_race_date(primary.get('date',''))}"

    subs = {
        "{{TITLE_DATE}}": TODAY.strftime("%a %d %b %Y"),
        "{{CYCLE_ROMAN}}": "I",
        "{{EDITION_NUM}}": str(TODAY.timetuple().tm_yday % 365),
        "{{DATE_LONG_WORDS}}": long_date_words(TODAY),
        "{{HERO_KICKER}}": hero_kicker,
        "{{HERO_DAYS}}": str(days_primary) if days_primary >= 0 else "—",
        "{{HERO_RACE_SHORT}}": hero_race_short,
        "{{HERO_DETAILS}}": hero_details,
        "{{HERO_QUOTE}}": primary.get("target", "Finish strong.") + " The first hour wins or loses the day.",
        "{{HERO_ATTR}}": f"Race plan, revised {TODAY.strftime('%d %b')}",
        "{{STATS_HTML}}": render_stats(activities, week_rows),
        "{{SEC_TODAY_META}}": f"Week {to_roman(week_n)} · {today_sec_meta}" if week_n else today_sec_meta,
        "{{TODAY_TAG}}": today_tag,
        "{{TODAY_TITLE_HTML}}": today_title_html,
        "{{TODAY_DETAIL_HTML}}": today_detail_html,
        "{{TODAY_META_HTML}}": today_meta_html,
        "{{TODAY_OBSERVATION}}": f"<strong>Today.</strong> {today_observation}",
        "{{INJURY_BANNER_HTML}}": render_injury_banner(injury_text),
        "{{WEEK_META}}": f"{week_range} · {week_label}" if week_n else "Current week",
        "{{WEEK_ROWS_HTML}}": render_week_rows(week_rows, activities_by_date),
        "{{LOG_ENTRIES_HTML}}": render_log_entries(activities),
        "{{LOG_OBSERVATION_HTML}}": f'<p class="observation"><strong>Note.</strong> Activity log refreshed at {NOW_ISO}.</p>',
        "{{RACES_META}}": f"{len(races)} on the calendar",
        "{{RACES_HTML}}": render_races(races),
        "{{TRENDS_HTML}}": trends_html,
        "{{EDITION_ROMAN_DATE}}": f"{TODAY.day}.{to_roman(TODAY.month)}.{TODAY.year}",
        "{{DATA_JSON}}": json.dumps({"charts": chart_data, "calendar": calendar_data}),
    }

    out = template_text
    for k, v in subs.items():
        out = out.replace(k, str(v))
    return out


def append_evolution_entry(activities: list[dict]) -> None:
    last_7 = [a for a in activities if a["date"] >= (TODAY - timedelta(days=7)).isoformat()]
    summary = f"{len(last_7)} activities in last 7 days, {len(activities)} in 90-day window."
    entry = f"""

---

## Cycle auto — {TODAY.isoformat()}

- **Sync at:** {NOW_ISO}
- **Activity baseline:** {summary}
- **Notes:** Auto-cycle.
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
