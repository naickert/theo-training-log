---
type: append-only-journal
updated: 2026-05-27
---

# Training Evolution Journal

The self-improvement log. Each daily dashboard run appends an entry here. Future runs read prior entries first so the dashboard evolves rather than regenerating identically.

## How to use this file

- Append-only. Newest entries at the bottom.
- Each entry: date, week of plan, what was completed, deviations from plan, observations, dashboard structural changes (if any).
- Keep entries terse — bullet points, not prose.
- If you change the dashboard structure (add/remove a panel), log why.

---

## Cycle 0 — 2026-05-27 (bootstrap)

- **Plan version:** Theo 3 Month Training Plan, revised 2026-05-27
- **Active races:** Imfolozi 55 km MTB (27 Jun, 31 days), Absa 10K (10 Jul, 44 days)
- **Foot:** ~90% PF recovery
- **Recent activity baseline (last 30 days):**
  - 2 runs, ~10 km total (Sun 10 May 5 km, Wed 20 May 5 km)
  - 5 bike sessions (4 in W6 cross-train week + 0 since 2 May MTB)
  - 5 weight sessions
- **Initial concern:** Bike volume since 2 May is zero. Imfolozi prep requires immediate ramp.
- **Dashboard structure (v1):** 8 panels — Today / This Week / Last 7 Days / Race Countdown / Trends / Foot Status / Next 4 Weeks / 3-Month Overview.
- **Next cycle should:** Test the plan-vs-actual diff logic against the actual W10 sessions (Wed bike intervals, Sat 30 km MTB, Sun 5 km run).

---

## Cycle 1 — 2026-05-29 (manual /my-training, Chrome sync)

- **Plan gate:** No revision needed. All 5 staleness triggers passed (no new race; injury log 27 May not newer than plan 28 May; next race 29d out; W10 25–31 May includes today; no `--revise-plan`).
- **Sync:** Chrome scrape of Strava training log. Reconciled against the repo's richer Strava-API dataset (has avg/max HR). No new activities vs the 28 May data — today's prescribed Bike tempo hasn't happened yet.
- **W10 completed so far:** Mon 25 Workout 1:36:44 ✅ · Tue 26 rest 💤 · Wed 27 🔁 substituted · Thu 28 Weights 50:38 ✅. Fri 29 (today) = Bike tempo prescribed.
- **Key deviation — Wed 27:** Prescribed *bike intervals*, instead ran 5.24 km @ 6:25/km **avg HR 182 / max 194** (+1.6 km opener). HR 182 ≈ LT — that's a threshold run, not easy. Hits tendency #1 (easy/quality creep) AND #3 (intervals → unstructured run), and it was run *hard on a 90%-healed PF foot* against the easy-only (HR ≤155) protocol. Foot held — 27 May injury log still "90% better", no flare.
- **Trend watch:** Bike 4wk fell 44→24 km (1 May Zwift aged out of the rolling 28-day window; nothing ridden since 2 May MTB). Imfolozi 29 days out → **Sat 30 May 30 km MTB is the ramp start and is critical.** Run vol flat at 17 km/4wk.
- **Data fix:** Deduped activities.json 62→52. Root cause: 27 May bootstrap used IDs like `2026-05-21_weight-training_...` while the 28 May API sync used `2026-05-21_morning-weight-training_...` — same activity, different slug, so they never merged (10 dup pairs: 8 weights + 1 MTB + 1 Zwift). Kept the strava_id+HR records; wrote clean file to skill-base **and** repo.
- **Dashboard structural changes this cycle:**
  1. Added **avg HR to run rows** in the week table (HR now available) — directly surfaces the #1 tendency (easy/threshold creep). First visible instance: Wed HR 182.
  2. Fixed **readiness-breakdown display bugs**: Imfolozi "Bike vol 4wk 0/150"→"24/150" (contradicted the 44 km stat tile); Amashova relabelled "Road bike 4wk" (0/200, MTB-excluded — honest); Hollywoodbets "Best pace 7:13"→"6:25/km" (7:13 was wrong).
  3. Fixed **Phase-3 arc progress** 0%→12% (was stuck at 0).
  4. Added **null-guard to calendar JS** — `calGrid` was removed from the layout on 28 May but the JS still called `cal.appendChild`, throwing at the end of the script.
- **Decisions taken this run (user answered):**
  1. **Pipelines → automated-only.** The GitHub Actions Strava-API job (`.github/workflows/daily-dashboard.yml`, 02:07 UTC daily) is now the single source of truth; the manual Chrome-scrape flow is retired. SKILL.md updated to match. (No local cron existed to remove — crons here are session-scoped.)
  2. **Readiness → documented formula.** Rewrote `compute_race_readiness` (build_dashboard.py) to a v2 model: weighted blend of physical-prep components vs race-specific targets, **no time-padding**. Documented in the function docstring + `scripts/build-dashboard.md`.
- **Engine fixes shipped to build_dashboard.py:** MTB-by-title categorization (2 May was mis-typed "bike" by Strava); avg HR on week-table rows; consistent rolling-28-day 4wk window (stats + readiness now agree); idempotent journal (≤1 auto entry/day — kills the spam vector). Also pruned the 25 spam entries from the repo journal and re-rendered today's dashboard from the fixed engine.
- **Readiness recalculated (v2):** Imfolozi **44** (at-risk), Absa **92** (on-track), Amashova **29** (at-risk), Hollywoodbets **73** (behind). Lower than the old padded 53/94/49/59 because the time term is gone — these now reflect actual physical prep, which honestly exposes the bike-volume gap (the real Imfolozi risk).
- **Next cycle should:** Confirm Sat 30 May 30 km MTB done (the bike ramp); flag Sun 31 easy run if avg HR >160.


---

## Cycle auto — 2026-05-29

- **Sync at:** 2026-05-29T06:03:58Z
- **Activity baseline:** 5 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.
