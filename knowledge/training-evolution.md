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


---

## Cycle 2 — 2026-05-29 (manual /my-training "update with latest strava data" · automated pipeline)

- **Mode:** First run under automated-only mode. Triggered `daily-dashboard.yml` (run 26621085636) → the **fixed** engine fetched fresh Strava, rebuilt, and pushed (`f058b79`); then pulled + reviewed.
- **New since this morning:** Fri 29 **bike tempo DONE** — "Zwift - Flat Out Fast in Watopia", 50:12, 16.82 km, **avg HR 136**. Indoor ride; avg HR 136 is aerobic-build (below the 155–165 tempo target, but consistent with the "not threshold" intent, and bike HR runs ~10 bpm under run HR). Counts as completed.
- **W10 status:** Mon workout ✅ · Tue rest 💤 · Wed 🔁 (ran hard, HR 182) · Thu weights ✅ · Fri bike tempo ✅ (Zwift). Sat 30 = 30 km MTB · Sun 31 = easy 5 km remain.
- **Trend movement:** Bike 4wk **24→41 km** (today's ride). Readiness: Imfolozi **44→49** (bike volume climbing toward 150), Amashova **29→32** (Zwift counts as road volume), Hollywoodbets 73, Absa 92 unchanged. Run vol flat 17 km.
- **Engine confirmed in CI:** the Action ran v2 readiness + mtb-by-title + idempotent journal correctly — 2 May re-categorised to mtb, 53 activities, zero dups, single auto entry/day. Automated-only handover successful.
- **Next:** **Sat 30 May 30 km MTB** is the key bike-ramp session — watch it lands. Flag Sun 31 easy run if avg HR >160 (the Wed-27 creep pattern).


---

## Cycle auto — 2026-05-30

- **Sync at:** 2026-05-30T03:19:54Z
- **Activity baseline:** 5 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle 3 — 2026-05-30 (manual /my-training · automated pipeline)

- **Plan gate:** No revision (W10 covers today; injury 27 May < plan 28 May; Imfolozi 28d out; no new race).
- **The big one landed:** Sat 30 **Long MTB DONE** — 29.14 km, 2:02:06, **avg HR 146, RE 258**. Matches the prescribed 30 km / ~2 hr / RPE 5–6 (aerobic). This is THE bike-ramp session flagged since Cycle 0 — captured by a midday manual trigger (the 05:19 scheduled run was too early).
- **W10 nearly complete:** Mon workout ✅ · Tue rest 💤 · Wed 🔁 (hard run, HR 182) · Thu weights ✅ · Fri bike tempo ✅ (Zwift) · Sat long MTB ✅. Only Sun 31 easy 5 km run left.
- **Trends:** This week **6.1h / 5 active days**. Bike 4wk **41→46 km** (2 May MTB aged out, 30 May MTB in); longest MTB **24→29 km**. Imfolozi readiness **49→56 — crossed at-risk → behind**. Amashova 32, Hollywoodbets 73, Absa 92. Run vol flat 17 km.
- **Observation:** Two solid bike days back-to-back (Fri Zwift + Sat 29 km MTB) — exactly the volume Imfolozi needs. Foot untested on the run since Wed; Sun's easy run is the next foot check.
- **Next:** Sun 31 easy 5 km — flag if avg HR >160 (the Wed-27 creep pattern). Then W11 (1–7 Jun): bike build, 40 km MTB on Sat 6 Jun. Readiness should keep climbing if the long rides land.


---

## Cycle auto — 2026-05-31

- **Sync at:** 2026-05-31T03:23:00Z
- **Activity baseline:** 6 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle 4 — 2026-05-31 (manual /my-training · automated pipeline)

- **Plan gate:** No revision (W10's last day; injury 27 May < plan 28 May; Imfolozi 27d; no new race).
- **W10 COMPLETE:** Mon workout ✅ · Tue rest 💤 · Wed 🔁 (hard run, HR 182) · Thu weights ✅ · Fri bike tempo ✅ · Sat long MTB ✅ · Sun easy run ⚠️ partial. Every key bike session landed — strong week for Imfolozi prep.
- **⚠️ Pattern fired again — easy-HR creep:** Sun 31 "easy 5 km" (target HR ≤155) run at **6:03/km, avg HR 177 / max 196** — the SECOND threshold-HR "easy" run this week (Wed 182, Sun 177). Tendency #1, twice in a week, on a 90%-PF foot. ⚠️ partial (right distance, wrong intensity). No pain logged (foot tolerating it), but easy-pace discipline (plan rule #1 / derailer #7) is the week's clear theme.
- **Dashboard evolution:** Added an **amber "HR n ⚠" flag** on week-table runs done on easy-prescribed days with avg HR >160 (prescribed interval/tempo/race runs exempt). Surfaces the creep at a glance; first triggered today. (`build_dashboard.py` → `render_week_rows`.)
- **Trends:** 6.6h / 6 active days. Run vol 17→22 km (Sun +5). Bike 46. Readiness: Imfolozi 56 (behind), Amashova 32 (at-risk), **Absa 92→97**, **Hollywoodbets 73→87** — both jumped because the fast 6:03/km run added run volume + a quick-pace data point. Caveat: the Hollywoodbets bump is partly a one-fast-5 km artifact; sub-60 still needs the structured Aug intervals, not fast "easy" runs.
- **Next (W11, 1–7 Jun · bike build):** Mon easy run · Wed bike intervals · Sat 40 km MTB. **Coaching priority: keep easy runs actually easy (HR ≤155)** — bank aerobic base + protect the foot; save speed for the prescribed sessions.


---

## Cycle 5 — 2026-05-31 (manual /my-training · dashboard evolution)

- **User request:** the week table should show "7-day history · today · 7 days plan ahead" instead of the fixed Mon–Sun calendar week (with a screenshot of the old view).
- **Change shipped** (`build_dashboard.py` + `templates/dashboard.html`): replaced the single-week table with a **rolling ±7-day window** (today−7 … today … today+7 = 15 rows). New `parse_plan_days()` maps every plan day-row across all week tables (and handles empty-detail rows like `| Weights | |`); new `build_rolling_window()` assembles the window. Section retitled **"Last 7 days · today · next 7"** with a date-range meta. Past days show actuals + status, today is highlighted in the middle, the next 7 show the upcoming plan (now spanning into W11). Days with no prescription (e.g. 24 May, pre-plan) render blank, never "Missed".
- **Why it's better:** one glance shows both what just happened and what's coming — the old Mon–Sun view showed zero days ahead on a Sunday.
- **Verified:** 15 rows (24 May → 7 Jun), today centred, amber HR-creep flag still fires on Sun (177), next-7 includes Sat 6 Jun 40 km MTB; 7 Jun "OR rest" styled as Rest.
- **No new training data this run** (same 54 activities as Cycle 4 — layout change only). W10 complete; W11 bike-build starts tomorrow.
