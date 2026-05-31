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
    # Strava sometimes records an MTB ride under the generic "Ride" type; recover
    # MTB from the activity title so road vs MTB stays distinct for race readiness.
    if category == "bike" and "mountain bike" in (a.get("name", "") or "").lower():
        category = "mtb"
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

def _yaml_strip(v: str) -> str:
    """Strip YAML inline comments and surrounding quotes."""
    # Remove inline comment after a space-then-hash (preserves URLs containing #)
    v = re.sub(r"\s+#.*$", "", v).strip()
    return v.strip('"').strip("'")


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
                current[k.strip()] = _yaml_strip(v)
        elif current is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = _yaml_strip(v)
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


def parse_plan_days(plan_text: str, year: int) -> dict:
    """Map EVERY plan day-row (across all week tables) to its prescription.
    Returns {iso_date: {"planned": str, "detail": str}}. Used by the rolling window
    so the table can span more than one plan week (history + next week's plan)."""
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    # Detail group is .*? (may be empty, e.g. "| Weights | |")
    row_re = re.compile(
        r"^\|\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*\|\s*(\d{1,2})\s+([A-Za-z]{3,})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|",
        re.MULTILINE)
    out: dict = {}
    for m in row_re.finditer(plan_text):
        mon = months.get(m.group(3)[:3].lower())
        if not mon:
            continue
        try:
            d = date(year, mon, int(m.group(2)))
        except ValueError:
            continue
        out[d.isoformat()] = {"planned": m.group(4).strip(), "detail": m.group(5).strip()}
    return out


def build_rolling_window(plan_text: str, today: date, back: int = 7, ahead: int = 7) -> list[dict]:
    """Rolling window: `back` days of history + today + `ahead` days of plan ahead.
    Row shape matches detect_week_block so render_week_rows / render_today_card work unchanged."""
    daymap = parse_plan_days(plan_text, today.year)
    rows = []
    for off in range(-back, ahead + 1):
        d = today + timedelta(days=off)
        info = daymap.get(d.isoformat(), {})
        rows.append({
            "day": d.strftime("%a"),
            "date": d.isoformat(),
            "date_label": f"{d.day} {d.strftime('%b')}",
            "planned": info.get("planned") or "—",
            "detail": info.get("detail", ""),
        })
    return rows


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


def compute_stats(activities: list[dict], week_rows: list[dict]) -> dict:
    """Returns dict of all top-of-page stat values.

    '4wk' windows use a rolling 28-day window (today + the prior 27 days), kept
    consistent with compute_race_readiness so the stat tiles and the race
    breakdowns never disagree.
    """
    week_start = TODAY - timedelta(days=TODAY.weekday())
    week_acts = [a for a in activities if week_start.isoformat() <= a["date"] <= TODAY.isoformat()]
    week_hours = sum(a["duration_sec"] for a in week_acts) / 3600
    active_days = len({a["date"] for a in week_acts})
    cutoff_4w = (TODAY - timedelta(days=27)).isoformat()
    acts_4w = [a for a in activities if a["date"] >= cutoff_4w]
    run_4w = sum(a["distance_km"] for a in acts_4w if a["category"] == "run")
    bike_4w = sum(a["distance_km"] for a in acts_4w if a["category"] in ("bike", "mtb"))
    rides = [a for a in activities if a["category"] in ("bike", "mtb") and a["distance_km"] > 0]
    last_ride = max(rides, key=lambda x: x["date"], default=None)
    if last_ride:
        days_since = (TODAY - date.fromisoformat(last_ride["date"])).days
        n_rides_4w = sum(1 for a in acts_4w if a["category"] in ("bike", "mtb") and a["distance_km"] > 0)
        bike_sub = f"{n_rides_4w} ride{'s' if n_rides_4w != 1 else ''} · last {days_since}d ago"
    else:
        bike_sub = "no rides logged"
    return {
        "hours": f"{week_hours:.1f}",
        "hours_sub": f"{active_days} active day{'s' if active_days != 1 else ''} this week",
        "run_km": f"{run_4w:.0f}",
        "run_sub": "post-PF rebuild",
        "bike_km": f"{bike_4w:.0f}",
        "bike_sub": bike_sub,
        "foot": "90",
        "foot_sub": "0/10 morning",
    }


def render_today_card(week_rows: list[dict]) -> dict:
    """Returns {title, detail_html, pills_html, icon_svg, sec_meta}."""
    today_row = next((r for r in week_rows if r["date"] == TODAY.isoformat()), None)
    if not today_row or today_row["planned"] in ("—",):
        return {
            "title": "Rest day",
            "detail_html": "No session prescribed. Recovery is training — sleep, hydrate, stretch.",
            "pills_html": '<span class="pill">Rest</span>',
            "icon_svg": '<svg viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
            "sec_meta": "Rest",
        }
    planned = today_row["planned"]
    detail = today_row["detail"]
    planned_clean = re.sub(r"~~(.+?)~~", r"\1", planned)
    planned_clean = re.sub(r"\*\*(.+?)\*\*", r"\1", planned_clean)
    detail_clean = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", detail)

    pills = []
    # Total session duration = the largest "N min" in the detail (components like
    # "15 min WU" are smaller than the "~50 min" total), not the first match.
    duration_vals = [int(x) for x in re.findall(r"(\d+)\s*min", detail)]
    if duration_vals: pills.append(("clock", f"~{max(duration_vals)} min"))
    hr_m = re.search(r"HR\s*(\d+[\s\-–]+\d+)", detail)
    if hr_m: pills.append(("heart", f"HR {hr_m.group(1).replace(' ','').replace('-','–')}"))
    rpe_m = re.search(r"RPE\s*(\d+(?:\s*[–-]\s*\d+)?)", detail)
    if rpe_m: pills.append(("flame", f"RPE {rpe_m.group(1)}"))

    mode_hints = {"bike":"Bike","mtb":"MTB","run":"Run","weights":"Weights","gym":"Gym"}
    mode = next((label for k,label in mode_hints.items() if k in planned.lower()), "Mixed")
    pills.append(("dot", mode))

    icon_svg_map = {
        "Bike": '<svg viewBox="0 0 24 24"><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M5 18l5-7 4 4 5-8"/></svg>',
        "MTB": '<svg viewBox="0 0 24 24"><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M5 18l5-7 4 4 5-8"/></svg>',
        "Run": '<svg viewBox="0 0 24 24"><circle cx="14" cy="4" r="2"/><path d="M11 13l-1 4 3 3 3-8-4-3-3 3-1 4M5 17l3-3"/></svg>',
        "Weights": '<svg viewBox="0 0 24 24"><path d="M6 4v16M18 4v16M2 8v8M22 8v8M6 8h12M6 16h12"/></svg>',
        "Gym": '<svg viewBox="0 0 24 24"><path d="M6 4v16M18 4v16M2 8v8M22 8v8M6 8h12M6 16h12"/></svg>',
    }
    icon_svg = icon_svg_map.get(mode, icon_svg_map["Run"])

    pill_html_pieces = []
    for i, (ico, text) in enumerate(pills):
        cls = "pill pill-lime" if i == 0 else "pill"
        ico_svg_map = {
            "clock": '<svg class="ico" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>',
            "heart": '<svg class="ico" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
            "flame": '<svg class="ico" viewBox="0 0 24 24"><path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-3 4-8 4-8z"/></svg>',
            "dot": '<svg class="ico" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/></svg>',
        }
        pill_html_pieces.append(f'<span class="{cls}">{ico_svg_map.get(ico, "")}{_esc(text)}</span>')
    pills_html = "".join(pill_html_pieces)

    return {
        "title": planned_clean,
        "detail_html": detail_clean,
        "pills_html": pills_html,
        "icon_svg": icon_svg,
        "sec_meta": f"Week · Day {TODAY.weekday()+1}",
    }


def render_foot_text(text: str) -> str:
    status_line = "Resolving — ~90% recovered. Daily prehab continues."
    if text:
        m = re.search(r"\*\*Current status:\*\*\s*([^\n]+)", text)
        if m:
            status_line = m.group(1)
    # Strip markdown links: [label](url) -> label
    status_line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", status_line)
    # Strip "See [doc]" trailing fragments
    status_line = re.sub(r"\s*See\s+[A-Z][\w-]+.*$", "", status_line, flags=re.IGNORECASE)
    # Cap at ~90 chars on a sentence boundary
    if len(status_line) > 90:
        sentences = re.split(r"(?<=[.!?])\s+", status_line)
        out, total = [], 0
        for s in sentences:
            if total + len(s) > 90 and out:
                break
            out.append(s); total += len(s) + 1
        status_line = " ".join(out)
    return _esc(status_line.strip())


def render_week_rows(week_rows: list[dict], activities_by_date: dict) -> str:
    out = []
    seen = set()
    for r in week_rows:
        d_iso = r["date"]
        d_obj = date.fromisoformat(d_iso)
        day_short = r["day"][:3].upper()
        day_num = d_obj.day
        planned = r["planned"]
        detail = r["detail"]
        is_today = (d_obj == TODAY)
        is_future = (d_obj > TODAY)

        # Planned column
        planned_clean = re.sub(r"~~(.+?)~~", r'<span class="strike">\1</span>', planned)
        planned_clean = re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", planned_clean)
        planned_cls = "week-planned"
        if "rest" in planned.lower() and "<span" not in planned_clean:
            planned_cls += " rest"

        # Actual column — dedupe activities for this date
        day_acts = []
        for a in activities_by_date.get(d_iso, []):
            key = (a["date"], a["title"], a["duration_sec"])
            if key in seen: continue
            seen.add(key)
            day_acts.append(a)

        if day_acts:
            items = []
            for a in day_acts:
                cat = a["category"]
                title = a["title"][:32]
                meta_bits = []
                if a["distance_km"] > 0:
                    meta_bits.append(f'<span class="val">{a["distance_km"]:.1f} km</span>')
                meta_bits.append(a["duration_display"])
                if a.get("pace_per_km"):
                    meta_bits.append(f"{a['pace_per_km']}/km")
                elif a.get("avg_speed_kmh"):
                    meta_bits.append(f"{a['avg_speed_kmh']} km/h")
                if a.get("relative_effort"):
                    meta_bits.append(f"RE {a['relative_effort']}")
                if a.get("avg_hr"):
                    # Flag easy-run HR creep (tendency #1): a run on a non-quality day with
                    # avg HR above the 155 easy cap (use 160 to allow surges) gets an amber
                    # warning. Prescribed quality runs (intervals/tempo/race) are exempt.
                    quality = any(w in planned.lower() for w in
                                  ("interval", "tempo", "threshold", "race", "stride", "800m", "400m", "1 km"))
                    if cat == "run" and a["avg_hr"] > 160 and not quality:
                        meta_bits.append(f'<span style="color:var(--amber);font-weight:600">HR {a["avg_hr"]} ⚠</span>')
                    else:
                        meta_bits.append(f"HR {a['avg_hr']}")
                icon = CATEGORY_ICON.get(cat, CATEGORY_ICON["other"])
                items.append(
                    f'<div class="week-actual-item">'
                    f'<span class="week-actual-ico {cat}">{icon}</span>'
                    f'<div class="week-actual-text">'
                    f'<span class="week-actual-title">{_esc(title)}</span>'
                    f'<span class="week-actual-meta">{" · ".join(meta_bits)}</span>'
                    f'</div>'
                    f'</div>'
                )
            actual_html = f'<div class="week-actual">{"".join(items)}</div>'
        else:
            if is_today:
                empty_text = "No activity yet"
            elif is_future:
                empty_text = ""
            elif "rest" in planned.lower() or "rest" in detail.lower():
                empty_text = "Rest taken"
            else:
                empty_text = "—"
            actual_html = f'<div class="week-actual empty">{empty_text}</div>'

        # Status pill
        if d_obj < TODAY:
            if planned.strip() in ("—", ""):
                # Nothing prescribed that day (e.g. before the plan starts) — never "missed"
                status, status_cls = ("Logged", "done") if day_acts else ("", "rest")
            elif day_acts and "rest" not in planned.lower():
                # Did the actual match the planned type? Simple keyword match
                planned_lower = planned.lower()
                act_cats = {a["category"] for a in day_acts}
                planned_match = False
                if ("bike" in planned_lower or "ride" in planned_lower) and act_cats & {"bike", "mtb"}:
                    planned_match = True
                elif "mtb" in planned_lower and "mtb" in act_cats:
                    planned_match = True
                elif "run" in planned_lower and "run" in act_cats:
                    planned_match = True
                elif "weight" in planned_lower and "weights" in act_cats:
                    planned_match = True
                elif "gym" in planned_lower and ("other" in act_cats or "weights" in act_cats):
                    planned_match = True
                if planned_match:
                    status, status_cls = "Complete", "done"
                else:
                    status, status_cls = "Substituted", "substituted"
            elif "rest" in planned.lower() or planned.lower().startswith("~~"):
                status, status_cls = "Rest", "rest"
            elif "done" in detail.lower():
                status, status_cls = "Complete", "done"
            else:
                status, status_cls = "Missed", "miss"
        elif is_today:
            status, status_cls = "Today", "today-mark"
        else:
            if "rest" in planned.lower():
                status, status_cls = "Rest", "rest"
            else:
                status, status_cls = "Upcoming", "upcoming"

        row_cls = " today-row" if is_today else (" future-row" if is_future else "")
        out.append(
            f'<div class="week-row{row_cls}">'
            f'<div class="week-day-cell"><span class="day">{day_short}</span><span class="num">{day_num}</span></div>'
            f'<div class="{planned_cls}">{planned_clean}</div>'
            f'{actual_html}'
            f'<div class="week-status-pill {status_cls}">{status}</div>'
            f'</div>'
        )
    return "".join(out)


CATEGORY_ICON = {
    "run": '<svg viewBox="0 0 24 24"><circle cx="14" cy="4" r="2"/><path d="M11 13l-1 4 3 3 3-8-4-3-3 3-1 4M5 17l3-3"/></svg>',
    "bike": '<svg viewBox="0 0 24 24"><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M5 18l5-7 4 4 5-8"/></svg>',
    "mtb": '<svg viewBox="0 0 24 24"><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M5 18l5-7 4 4 5-8"/></svg>',
    "weights": '<svg viewBox="0 0 24 24"><path d="M6 4v16M18 4v16M2 8v8M22 8v8M6 8h12M6 16h12"/></svg>',
    "other": '<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
    "walk": '<svg viewBox="0 0 24 24"><circle cx="14" cy="4" r="2"/><path d="M11 13l-1 4 3 3 3-8-4-3-3 3-1 4M5 17l3-3"/></svg>',
}


def render_week_actuals(week_rows: list[dict], activities_by_date: dict) -> str:
    """One row per day of this week, aligned with the plan column on the left."""
    out = []
    seen = set()
    for r in week_rows:
        d_iso = r["date"]
        d_obj = date.fromisoformat(d_iso)
        day_short = r["day"][:3].upper()
        day_num = d_obj.day
        is_today = (d_obj == TODAY)
        is_future = (d_obj > TODAY)
        # dedupe activities for this date
        day_acts = []
        for a in activities_by_date.get(d_iso, []):
            key = (a["date"], a["title"], a["duration_sec"])
            if key in seen: continue
            seen.add(key)
            day_acts.append(a)
        row_cls = " today-row" if is_today else ""
        day_cls = ""
        if is_today: day_cls = " today-day"
        elif is_future: day_cls = " future-day"
        if not day_acts:
            # Empty row — still rendered to align with plan
            empty_label = "Today — no activity yet" if is_today else ("Upcoming" if is_future else "No activity")
            out.append(
                f'<div class="actual-row{row_cls}">'
                f'<div class="actual-day{day_cls}"><span class="day">{day_short}</span><span class="num">{day_num}</span></div>'
                f'<div class="actual-body actual-empty">{empty_label}</div>'
                f'<div class="actual-stat"></div>'
                f'</div>'
            )
            continue
        # Render one row per activity (multiple per day will stack with shared day cell on first only)
        for i, a in enumerate(day_acts):
            cat = a["category"]
            title = a["title"][:36]
            meta_bits = []
            if a.get("pace_per_km"):
                meta_bits.append(f"{a['pace_per_km']}/km")
            elif a.get("avg_speed_kmh"):
                meta_bits.append(f"{a['avg_speed_kmh']} km/h")
            if a.get("relative_effort"):
                meta_bits.append(f"RE {a['relative_effort']}")
            meta = " · ".join(meta_bits) if meta_bits else CATEGORY_LABEL.get(cat, "Activity")
            if a["distance_km"] > 0:
                stat_val = f'{a["distance_km"]:.1f}'
                stat_sub = f"km · {a['duration_display']}"
            else:
                stat_val = a["duration_display"]
                stat_sub = "duration"
            icon = CATEGORY_ICON.get(cat, CATEGORY_ICON["other"])
            # Only first row of a multi-activity day shows the date label
            day_html = (
                f'<div class="actual-day{day_cls}"><span class="day">{day_short}</span><span class="num">{day_num}</span></div>'
                if i == 0 else
                f'<div class="actual-day actual-day-empty"></div>'
            )
            out.append(
                f'<div class="actual-row{row_cls}">'
                f'{day_html}'
                f'<div class="actual-body">'
                f'<div class="actual-title"><span class="actual-ico {cat}">{icon}</span>{_esc(title)}</div>'
                f'<div class="actual-meta">{_esc(meta)}</div>'
                f'</div>'
                f'<div class="actual-stat"><span class="val">{stat_val}</span><span class="sub">{stat_sub}</span></div>'
                f'</div>'
            )
    return "".join(out)


def compute_race_readiness(race: dict, activities: list[dict]) -> dict:
    """Race readiness, 0-100.

    Documented model (v2 — 2026-05-29). Readiness is a weighted blend of
    physical-preparedness components, each a ratio of (current / race-specific
    target) clamped to [0, 1]:

        pct = round(100 * Σ weightᵢ · clamp(actualᵢ / targetᵢ))

    Per-race weights sum to 1.0 (see each branch). Design rules:
      • NO "time remaining" term in the score. Time is shown separately as the
        countdown; padding the score with it (the v1 bug) inflated far-off races
        and masked real gaps such as low bike volume.
      • '4wk' = rolling 28-day window (today + prior 27 days), identical to
        compute_stats so tiles and breakdowns agree.
      • Road vs MTB are distinct categories (see normalize_activity); Amashova
        counts road only, Imfolozi counts bike+MTB.
      • 'fastest pace' = quickest run ≥3 km in the window (NOT the longest run's
        pace, which was the v1 'best pace 7:13' bug).
      • Foot factor = 0.90 (PF resolving; see injury-log).
    Status: ≥75 on-track · 50-74 behind · <50 at-risk.
    """
    days_to = race_days_to(race.get("date", ""))
    if days_to < 0:
        return {"pct": 100, "breakdown": [], "status": "past"}
    name = race.get("name", "")
    target = race.get("target", "") or ""

    # Dedup, then build the rolling 28-day window
    seen, acts = set(), []
    for a in activities:
        k = (a["date"], a["title"], a["duration_sec"])
        if k in seen:
            continue
        seen.add(k); acts.append(a)
    cutoff_4w = (TODAY - timedelta(days=27)).isoformat()
    acts_4w = [a for a in acts if a["date"] >= cutoff_4w]

    def clamp(x): return max(0.0, min(1.0, x))
    def longest(cats): return max((a["distance_km"] for a in acts if a["category"] in cats), default=0.0)
    def vol4w(cats): return sum(a["distance_km"] for a in acts_4w if a["category"] in cats)
    def fastest_pace_sec():
        paces = []
        for a in acts_4w:
            if a["category"] == "run" and a["distance_km"] >= 3 and a.get("pace_per_km"):
                mm, ss = a["pace_per_km"].split(":")
                paces.append(int(mm) * 60 + int(ss))
        return min(paces) if paces else None
    def blend(parts): return 100.0 * sum(w * clamp(r) for w, r in parts)
    FOOT = 0.90

    if "Imfolozi" in name or ("MTB" in name and str(race.get("distance_km", "")).startswith("5")):
        longest_mtb = longest({"mtb"})
        bike_vol = vol4w({"bike", "mtb"})
        pct = blend([(0.45, longest_mtb / 40), (0.45, bike_vol / 150), (0.10, FOOT)])
        breakdown = [
            ("Longest MTB", f"{longest_mtb:.0f}/40 km"),
            ("Bike vol 4wk", f"{bike_vol:.0f}/150 km"),
            ("Days to start", f"{days_to}"),
        ]
    elif "Amashova" in name or "106" in str(race.get("distance_km", "")):
        longest_road = longest({"bike"})           # road == non-MTB bike
        road_vol = vol4w({"bike"})
        pct = blend([(0.45, longest_road / 90), (0.45, road_vol / 200), (0.10, FOOT)])
        breakdown = [
            ("Longest road ride", f"{longest_road:.0f}/90 km"),
            ("Road bike 4wk", f"{road_vol:.0f}/200 km"),
            ("Days to start", f"{days_to}"),
        ]
    elif "Hollywoodbets" in name or "Sub-60" in target or "<60" in target:
        run_vol = vol4w({"run"})
        longest_run = longest({"run"})
        fp = fastest_pace_sec()
        pace_disp = fmt_pace(fp) if fp else "—"
        pace_ratio = clamp(1 - max(0, (fp or 450) - 359) / 91)   # 7:30/km -> 0%, 5:59/km -> 100%
        pct = blend([(0.40, pace_ratio), (0.30, run_vol / 30), (0.15, longest_run / 12), (0.15, FOOT)])
        breakdown = [
            ("Run vol 4wk", f"{run_vol:.0f}/30 km"),
            ("Longest run", f"{longest_run:.1f}/12 km"),
            ("Fastest pace 4wk", f"{pace_disp}/km vs 5:59"),
            ("Days to start", f"{days_to}"),
        ]
    elif "Absa" in name or "10K" in name:
        run_vol = vol4w({"run"})
        longest_run = longest({"run"})
        pct = blend([(0.40, longest_run / 10), (0.30, run_vol / 20), (0.30, FOOT)])
        breakdown = [
            ("Longest run", f"{longest_run:.1f}/8 km"),
            ("Run vol 4wk", f"{run_vol:.0f}/20 km"),
            ("Foot", f"{int(FOOT * 100)}%"),
        ]
    else:
        total_vol = vol4w({"run", "bike", "mtb"})
        pct = blend([(0.70, total_vol / 100), (0.30, FOOT)])
        breakdown = [("Total vol 4wk", f"{total_vol:.0f} km")]

    pct_int = int(round(pct))
    status = "on-track" if pct_int >= 75 else ("behind" if pct_int >= 50 else "at-risk")
    return {"pct": pct_int, "breakdown": breakdown, "status": status}


def render_races(races: list[dict], activities: list[dict]) -> str:
    out = []
    for i, r in enumerate(races):
        days = race_days_to(r.get("date",""))
        pri = (r.get("priority") or "").upper()
        if i == 0:
            cls = "primary"
            priority_label = "A-Race · Peak"
        elif pri == "B":
            cls = "secondary"
            priority_label = "B-Race"
        elif pri == "C":
            cls = "secondary"
            priority_label = "Tune-up"
        else:
            cls = "secondary"
            priority_label = "A-Race"

        name = r.get("name", "")
        long_dt = long_race_date(r.get("date",""))
        location = r.get("location","")
        date_line = f"{long_dt}{(' · ' + location) if location else ''}"
        target_line = r.get("target", "")
        days_str = str(days) if days >= 0 else "—"

        readiness = compute_race_readiness(r, activities)
        # Inline SVG progress ring
        pct = readiness["pct"]
        circ_circumference = 100.5  # 2 * pi * r=16
        offset = circ_circumference * (1 - pct / 100)
        status_cls = readiness["status"]
        ring_color = {"on-track": "currentColor", "behind": "currentColor", "at-risk": "currentColor"}[status_cls]
        breakdown_html = "".join(f'<span class="ready-bd-item"><span class="ready-bd-k">{_esc(k)}</span><span class="ready-bd-v">{_esc(v)}</span></span>' for k, v in readiness["breakdown"])

        ring_svg = (
            f'<svg viewBox="0 0 40 40" class="ready-ring">'
            f'<circle cx="20" cy="20" r="16" class="ready-ring-bg"></circle>'
            f'<circle cx="20" cy="20" r="16" class="ready-ring-fg" '
            f'stroke-dasharray="{circ_circumference}" stroke-dashoffset="{offset:.1f}"></circle>'
            f'</svg>'
        )

        out.append(
            f'<div class="race-card {cls}" data-readiness="{status_cls}">'
            f'<div class="race-card-top">'
            f'<span class="race-priority">{_esc(priority_label)}</span>'
            f'<div class="ready-badge">{ring_svg}<span class="ready-pct">{pct}<small>%</small></span></div>'
            f'</div>'
            f'<h3 class="race-name">{_esc(name)}</h3>'
            f'<div class="race-date">{_esc(date_line)}</div>'
            f'<div class="race-countdown-row"><span class="race-countdown">{days_str}</span><span class="race-countdown-unit">days · ready</span></div>'
            f'<p class="race-target"><strong>{_esc(target_line)}</strong></p>'
            f'<div class="ready-breakdown">{breakdown_html}</div>'
            f'</div>'
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


def render_trends(weekly: list[dict]) -> tuple[str, dict]:
    latest = weekly[-1] if weekly else {"hours":0,"runKm":0,"bikeKm":0,"longestMin":0}
    prev = weekly[-2] if len(weekly) > 1 else latest
    def delta_class(now, then):
        if now > then * 1.1: return "up"
        if now < then * 0.9 and then > 0: return "down"
        return ""
    def delta_text(now, then, unit):
        if then == 0:
            return "+" if now > 0 else "—"
        direction = "↑" if now > then else ("↓" if now < then else "→")
        return f"{direction} {abs(now-then):.1f}{unit} vs last wk"

    hours_chart = [round(w["hours"],1) for w in weekly]
    run_chart = [round(w["runKm"],1) for w in weekly]
    bike_chart = [round(w["bikeKm"],1) for w in weekly]
    longest_chart = [int(w["longestMin"]) for w in weekly]

    return (
        f'<div class="trend-card">'
        f'<div class="trend-label">Weekly Hours</div>'
        f'<div class="trend-val">{latest["hours"]:.1f}<small>h</small></div>'
        f'<div class="trend-delta {delta_class(latest["hours"],prev["hours"])}">{delta_text(latest["hours"],prev["hours"],"h")}</div>'
        f'<div class="trend-chart"><canvas id="chartHours"></canvas></div>'
        f'</div>'
        f'<div class="trend-card">'
        f'<div class="trend-label">Run · km</div>'
        f'<div class="trend-val">{latest["runKm"]:.1f}<small>km</small></div>'
        f'<div class="trend-delta {delta_class(latest["runKm"],prev["runKm"])}">{delta_text(latest["runKm"],prev["runKm"],"km")}</div>'
        f'<div class="trend-chart"><canvas id="chartRun"></canvas></div>'
        f'</div>'
        f'<div class="trend-card">'
        f'<div class="trend-label">Bike · km</div>'
        f'<div class="trend-val">{latest["bikeKm"]:.1f}<small>km</small></div>'
        f'<div class="trend-delta {delta_class(latest["bikeKm"],prev["bikeKm"])}">{delta_text(latest["bikeKm"],prev["bikeKm"],"km")}</div>'
        f'<div class="trend-chart"><canvas id="chartBike"></canvas></div>'
        f'</div>'
        f'<div class="trend-card">'
        f'<div class="trend-label">Longest · min</div>'
        f'<div class="trend-val">{int(latest["longestMin"])}<small>min</small></div>'
        f'<div class="trend-delta">need 3hr+ ride soon</div>'
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

def greeting_verb() -> str:
    h = datetime.now(SAST).hour
    if h < 12: return "Good morning"
    if h < 17: return "Good afternoon"
    return "Good evening"


def render_arc(week_n: int) -> str:
    """Render the 3-month phase timeline. week_n is the current week number."""
    phases = [
        {
            "name": "Phase 3 · Imfolozi build",
            "weeks": list(range(10, 15)),
            "label": "W10–W14",
            "dates": "25 May – 28 Jun",
            "goal": "Build to 40 km MTB · stage rehearsal",
            "race": {"name": "Imfolozi", "date": "27 Jun", "icon": "★"},
            "class": "p3",
        },
        {
            "name": "Phase 4 · Amashova pivot",
            "weeks": list(range(15, 18)),
            "label": "W15–W17",
            "dates": "29 Jun – 19 Jul",
            "goal": "MTB → road bike · build to 90 km road",
            "race": {"name": "Amashova", "date": "19 Jul", "icon": "★"},
            "class": "p4",
        },
        {
            "name": "Phase 5 · Sub-60 build",
            "weeks": list(range(18, 24)),
            "label": "W18–W23",
            "dates": "20 Jul – 30 Aug",
            "goal": "Run base → intervals → race pace",
            "race": {"name": "Hollywoodbets", "date": "30 Aug", "icon": "★"},
            "class": "p5",
        },
    ]

    cards = []
    for p in phases:
        is_current = week_n in p["weeks"]
        is_past = week_n > max(p["weeks"])
        if is_current:
            state = "current"
            state_label = "Active"
        elif is_past:
            state = "done"
            state_label = "Done"
        else:
            state = "upcoming"
            state_label = "Upcoming"
        # Progress within phase
        if is_current:
            done_weeks = (week_n - min(p["weeks"]))
            total_weeks = len(p["weeks"])
            progress = int(round(100 * done_weeks / max(total_weeks, 1)))
        elif is_past:
            progress = 100
        else:
            progress = 0
        cards.append(
            f'<div class="arc-phase {p["class"]} {state}">'
            f'<div class="arc-state">{state_label}</div>'
            f'<div class="arc-name">{p["name"]}</div>'
            f'<div class="arc-dates">{p["dates"]} · {p["label"]}</div>'
            f'<div class="arc-goal">{p["goal"]}</div>'
            f'<div class="arc-progress"><div class="arc-progress-fill" style="width:{progress}%"></div></div>'
            f'<div class="arc-race"><span class="arc-race-icon">{p["race"]["icon"]}</span><span>{p["race"]["name"]} · {p["race"]["date"]}</span></div>'
            f'</div>'
        )
    return "".join(cards)


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
    # Rolling window for the main table: last 7 days + today + next 7 planned days.
    rolling_rows = build_rolling_window(plan_text, TODAY, back=7, ahead=7)

    activities_by_date = defaultdict(list)
    for a in activities:
        activities_by_date[a["date"]].append(a)

    today_card = render_today_card(rolling_rows)
    weekly = compute_weekly_buckets(activities, 12)
    trends_html, chart_data = render_trends(weekly)
    calendar_data = build_calendar_data(activities, races)
    stats = compute_stats(activities, week_rows)

    # Last 8 weeks of stats for sparklines
    sparks = {
        "hours": [round(w["hours"],1) for w in weekly[-8:]],
        "runKm": [round(w["runKm"],1) for w in weekly[-8:]],
        "bikeKm": [round(w["bikeKm"],1) for w in weekly[-8:]],
    }

    race_name = primary.get("name", "")
    hero_race_short = "iMfolozi" if "Imfolozi" in race_name else (race_name.split()[0] if race_name else "race")
    distance_km = primary.get("distance_km", "")
    sport_type = primary.get("type","race").lower()
    hero_details = f"{distance_km} km {sport_type} · {long_race_date(primary.get('date',''))}"

    subs = {
        "{{TITLE_DATE}}": TODAY.strftime("%a %d %b %Y"),
        "{{DATE_LONG}}": long_date_words(TODAY),
        "{{GREETING_VERB}}": greeting_verb(),
        "{{NOW_ISO}}": NOW_ISO,
        "{{HERO_DAYS}}": str(days_primary) if days_primary >= 0 else "—",
        "{{HERO_RACE_NAME}}": race_name,
        "{{HERO_RACE_SHORT}}": hero_race_short,
        "{{HERO_RACE_DETAILS}}": hero_details,
        "{{HERO_QUOTE}}": primary.get("target", "Finish strong."),
        "{{STAT_HOURS}}": stats["hours"],
        "{{STAT_HOURS_SUB}}": stats["hours_sub"],
        "{{STAT_RUN_KM}}": stats["run_km"],
        "{{STAT_RUN_SUB}}": stats["run_sub"],
        "{{STAT_BIKE_KM}}": stats["bike_km"],
        "{{STAT_BIKE_SUB}}": stats["bike_sub"],
        "{{STAT_FOOT}}": stats["foot"],
        "{{STAT_FOOT_SUB}}": stats["foot_sub"],
        "{{TODAY_TITLE}}": today_card["title"],
        "{{TODAY_DETAIL_HTML}}": today_card["detail_html"],
        "{{TODAY_PILLS}}": today_card["pills_html"],
        "{{TODAY_ICON_SVG}}": today_card["icon_svg"],
        "{{FOOT_BODY}}": render_foot_text(injury_text),
        "{{WEEK_TITLE}}": "Last 7 days · today · next 7",
        "{{WEEK_META}}": f"{rolling_rows[0]['date_label']} → {rolling_rows[-1]['date_label']} · history + plan ahead",
        "{{WEEK_ROWS_HTML}}": render_week_rows(rolling_rows, activities_by_date),
        # LOG_ENTRIES_HTML no longer used — actuals merged into week table
        "{{RACES_META}}": f"{len(races)} on the calendar",
        "{{RACES_HTML}}": render_races(races, activities),
        "{{TRENDS_HTML}}": trends_html,
        "{{DATA_JSON}}": json.dumps({"sparks": sparks, "charts": chart_data, "calendar": calendar_data}),
        "{{ARC_HTML}}": render_arc(week_n),
    }

    out = template_text
    for k, v in subs.items():
        out = out.replace(k, str(v))
    return out


def append_evolution_entry(activities: list[dict]) -> None:
    if not EVOLUTION.exists():
        return
    existing = EVOLUTION.read_text()
    # Idempotent: at most one auto entry per day, even if the workflow runs/dispatches
    # multiple times. (The 27-28 May journal spam came from repeated dispatches.)
    if f"## Cycle auto — {TODAY.isoformat()}" in existing:
        return
    last_7 = [a for a in activities if a["date"] >= (TODAY - timedelta(days=7)).isoformat()]
    summary = f"{len(last_7)} activities in last 7 days, {len(activities)} in 90-day window."
    entry = f"""

---

## Cycle auto — {TODAY.isoformat()}

- **Sync at:** {NOW_ISO}
- **Activity baseline:** {summary}
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.
"""
    EVOLUTION.write_text(existing + entry)


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
