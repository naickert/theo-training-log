---
type: source-of-truth
updated: 2026-07-23
---

# Race Calendar — Theo

The canonical list of all registered races. The dashboard reads this file to compute days-to-race and to populate race-prep panels.

## Format

Each race is a YAML entry. Required fields: `name`, `date` (YYYY-MM-DD), `type`, `priority` (A/B/C). Optional: `distance_km`, `target`, `prep_doc`, `location`, `start_time`, `notes`.

## Active Races

```yaml
- name: Hollywoodbets Durban 10K
  date: 2026-08-30
  type: Run
  distance_km: 10
  priority: A
  location: Durban, KZN
  start_time: Sunday morning (TBC)
  target: Sub-60 attempt — under 60:00
  notes: Registered. Order HB-20260528-ZLJMZD. Race pack collection 27-29 Aug at Hollywoodbets Kingsmead. Race number via SMS/WhatsApp in race week. This is the season's sub-60 target — replaces the Sept/Oct placeholder.
```

## How to add a new race

Either edit this file directly, or in a Claude conversation say "add race X on date Y" and the skill will append to this list and update the dashboard on next run.

## Past races (auto-moved here when date < today by >7 days)

```yaml
- name: Amashova National Classic
  date: 2026-07-19
  type: Road Cycling
  distance_km: 106
  priority: A
  location: Pietermaritzburg → Durban, KZN
  target: Finish strong, ~4-4.5 hr
  result: Not on Strava as of 2026-07-22 sync (96hr post-race) — outcome pending upload or race not completed. Check Garmin/Wahoo manual upload.
  notes: Registered Open/Seeded (R800). Entry WEB-5235-854733. Moved to Past 2026-07-23 — race date passed, result unconfirmed. Phase 4 complete.

- name: Absa 10K Road
  date: 2026-07-10
  type: Run
  distance_km: 10
  priority: C
  target: Easy effort ~1:08–1:10 (tune-up only; do not race)
  result: No Strava upload as of 2026-07-11 — outcome TBC (race occurred; result pending upload)
  notes: Recovery tune-up between Imfolozi and Amashova. Moved to Past on 2026-07-11; no activity appeared in Strava sync. If race was not run, note here.

- name: Imfolozi 55 km MTB (Stage Race)
  date: 2026-06-27
  type: MTB
  distance_km: 55
  priority: A
  location: Hluhluwe-iMfolozi Game Reserve, KZN
  result: COMPLETED — Stage 1 40.6 km / 3:08 / avg HR 163 · Stage 2 11.9 km / 48 min / avg HR 147
  notes: 2-day stage race. Both stages completed. Foot held across both days.
```
