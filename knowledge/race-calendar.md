---
type: source-of-truth
updated: 2026-05-27
---

# Race Calendar — Theo

The canonical list of all registered races. The dashboard reads this file to compute days-to-race and to populate race-prep panels.

## Format

Each race is a YAML entry. Required fields: `name`, `date` (YYYY-MM-DD), `type`, `priority` (A/B/C). Optional: `distance_km`, `target`, `prep_doc`, `location`, `start_time`, `notes`.

## Active Races

```yaml
- name: Imfolozi 55 km MTB
  date: 2026-06-27
  type: MTB
  distance_km: 55
  priority: A
  target: Finish strong, ~4 hr
  location: iMfolozi Game Reserve, KZN
  prep_doc: /Users/theonaicker/Documents/Claude/Quick_Projects/Personal/Running/Imfolozi-55km-Race-Prep.md
  notes: First time at this distance. Format (1-day vs 2-day stage) to be confirmed with organisers.

- name: Absa 10K Road
  date: 2026-07-10
  type: Run
  distance_km: 10
  priority: B
  target: 1:02–1:05 (foot & fitness dependent)
  notes: Real road race test post-Imfolozi recovery. Tune-up before Amashova 9 days later.

- name: Amashova National Classic
  date: 2026-07-19
  type: Road Cycling
  distance_km: 106
  priority: A
  location: Pietermaritzburg → Durban, KZN
  start_time: Sunday morning (TBC)
  target: Finish strong, ~4-4.5 hr
  notes: Registered Open/Seeded (R800). Entry WEB-5235-854733, Payment WEB_2143719. R140 permanent FinishTime board + R70 CSA day licence. Famous PMB→Durban road race. 22 days after Imfolozi MTB, 9 days after Absa 10K.

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

(none yet)
