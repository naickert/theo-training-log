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


---

## Cycle auto — 2026-06-01

- **Sync at:** 2026-06-01T03:25:04Z
- **Activity baseline:** 7 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle auto — 2026-06-02

- **Sync at:** 2026-06-02T03:25:28Z
- **Activity baseline:** 6 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle auto — 2026-06-03

- **Sync at:** 2026-06-03T03:24:42Z
- **Activity baseline:** 7 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle auto — 2026-06-04

- **Sync at:** 2026-06-04T03:24:46Z
- **Activity baseline:** 6 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle auto — 2026-06-06

- **Sync at:** 2026-06-06T03:19:51Z
- **Activity baseline:** 4 activities in last 7 days, 51 in 90-day window.
- **Notes:** Auto-cycle (GitHub Actions). Manual /my-training cycles are logged separately.


---

## Cycle 6 — 2026-06-06 (manual /my-training · automated pipeline)

- **Plan gate:** No revision (W11 covers today; injury 27 May < plan 28 May; Imfolozi 21d; no new race). 6-day gap since Cycle 5 — daily auto-builds ran fine (1–6 Jun commits all present).
- **Today landed:** Sat 6 **Long MTB ✅** — 36.86 km, 2:12:21, avg HR 141 (92% of the 40 km target, aerobic). Second big MTB in 8 days.
- **⚠️ But W11 was light/disrupted:** Mon 1 easy run ❌ · Tue 2 weights → short 30 min ride (substituted) · Wed 3 bike intervals → easy 31 min ride HR 133 (not intervals) · Thu 4 weights ❌ · Fri 5 bike tempo ❌ · Sat 6 MTB ✅. Three missed sessions; weekly volume halved (6.6→3.2 h); no running since 31 May.
- **Net effect — Imfolozi fine:** the two long MTBs (30 May 29 km + 6 Jun 37 km) pushed **Imfolozi readiness 56→75 (now on-track)** — longest MTB 37/40, bike vol 83/150. For a "finish strong" stage race the long aerobic rides are what count, so the missed weekday quality matters less here.
- **What the misses cost:** run base + foot work stalled (no run since 31 May) — a Hollywoodbets/sub-60 concern, but that's 85 days out. Absa 97, Hollywoodbets 87 (carried from late-May runs), Amashova 32 (laggard — needs road rides post-Imfolozi).
- **No dashboard change this cycle** — the rolling window + Missed/Substituted flags already surface the light week clearly; no gratuitous change.
- **Next:** Sun 7 easy run OR rest — first run in a week; flag if HR >160. **W12 (8–14 Jun) = Imfolozi stage-sim weekend** (Sat 40 km dress rehearsal + Sun 15 km back-to-back). If weekday sessions keep slipping, protect the long rides — they're carrying the prep.


---

## Cycle auto — 2026-06-07

- **Sync at:** 2026-06-07T03:10:13Z
- **Data source:** Strava API
- **Activity baseline:** 4 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-08

- **Sync at:** 2026-06-08T03:10:12Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 51 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 7 — 2026-06-08 (manual · W12 stage-sim week start)

- **Plan calibration (trigger e):** `race-calendar.md` had Absa 10K at priority B / target 1:02–1:05, contradicting the plan (updated 2026-05-28) which demoted it to C tune-up / ~1:08–1:10. Calendar corrected; plan `updated:` bumped to 2026-06-08. Obsidian local mirror needs manual sync.
- **ACWR 1.02** — optimal (acute RE 295, chronic weekly avg 290). No spike.
- **W11 adherence 3/7** (Tue bike, Wed short ride, Sat MTB 36.9 km) — mirrors W11 pattern flagged in Cycle 6. No run since 31 May (8 days).
- **W12 kicks off today** — the critical stage-sim week. Sat 13 Jun = 40 km dress rehearsal, Sun 14 Jun = 15 km back-to-back. Imfolozi 19 days away. If weekday sessions slip again, protect the Sat/Sun simulation blocks — they are the non-negotiable.
- **⚠️ Easy-run HR pattern persists:** May 20 HR 168, May 27 HR 182, May 31 HR 177 — all prescribed "easy" runs, all above the 155 ceiling, two well above 170. No foot pain reported since 27 May, but the re-flare window is still open given PF history. If today's Mon easy 6 km run lands, flag the HR.
- **Next:** Watch today's Mon easy run HR + Sat/Sun Stage 1/2 sim completion.


---

## Cycle auto — 2026-06-09

- **Sync at:** 2026-06-09T03:09:06Z
- **Data source:** Strava API
- **Activity baseline:** 4 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 8 — 2026-06-09 (manual · W12 stage-sim week · Mon HR flag fired)

- **Plan gate:** No revision. W12 (8–14 Jun) covers today; injury log (27 May) older than plan (8 Jun); Imfolozi 18d (not <7); all races in plan.
- **Mon Jun 8 easy-run HR breach confirmed:** 5.03 km @ 5:48/km, avg HR **180** / max 199. Plan: easy 6 km, HR ≤155. This is the 4th consecutive easy-run HR breach (May 20: 168 · May 27: 182 · May 31: 177 · Jun 8: 180) — all prescribed Z2 runs executed at Z4/LT. Critical given active PF recovery. No foot pain reported, but the re-flare window is open until physio clearance.
- **ACWR 1.28** — jumped from 1.02 yesterday as Mon's run (RE 138) entered the 7-day acute window. Still inside the safe band (0.8–1.3) but at the upper edge; a hard session today would push it borderline.
- **W11 adherence 1/5** key cardio sessions to standard (Sat MTB 37 km ✅; Mon run missed; Wed intervals → easy ride HR 133; Fri tempo missed; Thu weights missed). Long MTBs (29 km + 37 km) are carrying Imfolozi readiness despite the mid-week gaps.
- **Imfolozi 18 days out:** readiness ~75% (Cycle 6). Non-negotiables this week: Wed bike intervals (4×8 min @HR 165–175) + Sat Stage 1 Sim 40 km dress rehearsal + Sun Stage 2 Sim 15 km back-to-back. If weekday sessions slip again, protect Sat/Sun — they are the race-prep deliverables.
- **Foot status:** no new entry in injury-log since 27 May ("90% better"). Foot tolerating the hard easy-runs without logged pain, but the consistent HR overshoot is the structural risk factor.
- **Next:** Watch Sat 13 Jun Stage 1 Sim completion (40 km) and HR discipline on Wed bike intervals.


---

## Cycle auto — 2026-06-10

- **Sync at:** 2026-06-10T04:25:07Z
- **Data source:** Strava API
- **Activity baseline:** 4 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-11

- **Sync at:** 2026-06-11T00:12:08Z
- **Data source:** Strava API
- **Activity baseline:** 4 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 9 — 2026-06-11 (manual · W12 Stage-Sim eve · ACWR Caution)

- **Plan gate:** No revision. W12 (8–14 Jun) covers today; injury log (27 May) older than plan (8 Jun); Imfolozi 16 days out (not <7); all races reflected.
- **⚠️ ACWR 1.47 — Caution zone** (acute RE 537, chronic avg 366/wk). Jumped from 1.28 on Jun 9 as Jun 6 MTB (RE 232) now anchors the acute week alongside Mon run (RE 138) and Wed Zwift (RE 146). Safe band = 0.8–1.3; 1.47 approaches the 1.5 injury-risk spike threshold. This is the worst timing: Stage Sim weekend (Sat 40 km + Sun 15 km) is 2 days away and will spike ACWR further.
- **Risk mitigation:** Stage Sim is non-negotiable — execute at RPE 5–6 first two-thirds (not harder), no hero efforts. Today's (Thu) weights session should proceed but no added cardio. Fri bike tempo — keep HR ≤155, treat as active recovery not an extra quality day.
- **W12 so far:** Mon run ⚠️ HR 180 (≤155 target, 4th breach), Tue weights ✅, Wed bike intervals ⚠️ (Zwift "Threshold Hold" 52:49 avg HR 152 — shorter and lower-intensity than 4×8min @165–175 prescribed). The quality stimulus for Stage Sim week was underdelivered mid-week.
- **Adherence 11/14** (4-week, 79%) — long MTBs (29, 37 km) carrying Imfolozi readiness to **81%** (on-track). Mid-week sessions (bike intervals, Fri tempos) continue to slip.
- **Foot:** No new injury-log entry since 27 May ("90% better"). Prehab must stay daily through Stage Sim and race week — ACWR near-spike + PF history = elevated re-flare risk.
- **Next:** Sat 13 Jun Stage 1 Sim 40 km + Sun 14 Jun Stage 2 Sim 15 km. Execute controlled. Watch HR on back-to-back to avoid additional overreach.


---

## Cycle auto — 2026-06-12

- **Sync at:** 2026-06-12T00:12:05Z
- **Data source:** Strava API
- **Activity baseline:** 5 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-13

- **Sync at:** 2026-06-13T00:09:13Z
- **Data source:** Strava API
- **Activity baseline:** 5 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-14

- **Sync at:** 2026-06-14T00:09:17Z
- **Data source:** Strava API
- **Activity baseline:** 5 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 10 — 2026-06-14 (manual · W12 final day · Stage 1 Sim miss · Imfolozi 13d)

- **Plan gate:** Current. W12 (8–14 Jun) covers today; injury log (27 May) older than plan (8 Jun); Imfolozi 13d out (not <7 — next week is the taper); all 4 races in plan.
- **⚠️ STAGE 1 DRESS REHEARSAL MISSED:** Sat 13 Jun plan = 40 km outdoor MTB, race kit, race bike, race nutrition — the ONLY back-to-back ride scheduled before Imfolozi. Actual = Zwift "Big Loop in Watopia" 20.09 km, 1:37, avg HR 146. Race nutrition has NOT been rehearsed; race-kit fit on bike has NOT been tested outdoors. Imfolozi 13 days away.
- **ACWR 1.25 — recovered into safe band** (acute 529, chronic avg 422). Cycle 9 flagged 1.47 caution; Jun 6 MTB (RE 232) aged out of the acute window and Jun 13 Zwift (RE 209) replaced it. No current load spike, but Stage 2 Sim today + Imfolozi race week will continue loading.
- **W12 adherence (6 of 7 days done):** Mon run ⚠️ HR 180 (4th consecutive easy-run breach, ≤155 target) · Tue weights ✅ · Wed Zwift threshold 52:49 ⚠️ (shorter than 4×8 min prescribed) · Thu weights ✅ · Fri tempo ❌ · Sat Stage 1 Sim ⚠️ (Zwift 20 km indoor, not 40 km outdoor dress rehearsal) · Sun Stage 2 Sim TBD.
- **4-week adherence ~68%:** W9 43% · W10 100% · W11 57% · W12 71% (partial). Mid-week quality sessions (Fri tempos, full bike intervals) are the consistent gap; long rides are carrying Imfolozi readiness.
- **Bike vol 4wk: 122.9 km / 150 km target.** Longest outdoor MTB: 36.86 km (Jun 6) — not yet at the 40–50 km dress-rehearsal standard. The Zwift rides are supplementing but not substituting for trail-specific prep.
- **Foot:** No new injury-log entry since 27 May. Tolerating high-HR runs without logged pain, but the 4 consecutive easy-run HR breaches (168, 182, 177, 180) on a PF-recovering foot remain the primary re-flare risk.
- **Priority actions before Imfolozi:** (1) Complete Stage 2 Sim today (15 km outdoor MTB, 07:30). (2) Do a short outdoor nutrition rehearsal ride in W13 (20–25 km is enough to test the gel/bottle protocol). (3) Keep W13 easy bike + foot prehab daily — ACWR will naturally peak from race-week loading.
