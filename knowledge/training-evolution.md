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


---

## Cycle auto — 2026-06-15

- **Sync at:** 2026-06-15T00:11:56Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 11 — 2026-06-15 (manual · W12 complete · W13 freshen starts · ACWR caution re-triggered)

- **Plan gate:** Current. W13 (15–21 Jun) covers today; injury log (27 May) older than plan (8 Jun); Imfolozi 12d out (not <7); all 4 races in plan.
- **W12 COMPLETE — Stage Sim outcome:** Both sims done on Zwift indoors. Sat 13 = Zwift 20 km / 1:37 / avg HR 146 (vs. 40 km outdoor MTB prescribed). Sun 14 = Zwift Coast Crusher 42.6 km / 1:51 / avg HR 155 (vs. 15 km outdoor MTB prescribed). Volume on Sun exceeded target; but **no outdoor trail riding, no race-kit fit test, no nutrition rehearsal executed**. This is the critical gap 12 days out.
- **⚠️ ACWR 1.46 — caution zone re-entered** (acute 7d RE 731, chronic avg 502/wk). Sun Jun 14 Zwift (RE 340) spiked the acute load — same caution level as Cycle 9 (1.47). W13 is freshen week by design; volume should drop naturally. Do not add extra sessions.
- **Milestone: Bike vol 4wk 165.5 km ≥ 150 km target ✓** — Imfolozi bike-volume readiness criterion met for the first time. Long MTBs (29, 37 km) + Zwift cross-training got there.
- **4-week adherence ~68%:** W9 43% · W10 100% · W11 57% · W12 71%. Mid-week quality (Fri tempos, full bike intervals) remains the consistent gap. Long rides carrying the prep.
- **Easy-run HR breaches: 4 consecutive** (May 20: 168 · May 27: 182 · May 31: 177 · Jun 8: 180 — all prescribed ≤155). No foot pain logged. PF risk remains elevated with ACWR at 1.46.
- **W13 priority actions (non-negotiable before Imfolozi):** (1) **Sat 20 Jun — MTB 25–30 km outdoors with race nutrition**: gel at 45 min, bottle every 45 min, race kit on bike — this is the only remaining opportunity for an outdoor dress rehearsal. (2) **Mon 15 Jun easy run** — keep HR ≤155; break the breach streak. (3) **Wed bike session** — last quality ride; controlled, HR ≤180, don't add load. (4) Daily foot prehab — non-negotiable.

---

## Cycle 12 — 2026-06-15 (manual · health-screen integration · plan revised)

- **Notable event:** folded the **15 Jun executive health screen** into the plan (see [[theo-health-screen-review-2026-06-15]]). This is the new input today; Cycle 11 (earlier) already covered the load/adherence review.
- **Health read (athlete-relevant):** broadly clean and *confirms good systemic load tolerance* — normal FT3 (no energy-deficiency signal), healthy total testosterone, **ferritin 68.8 / TSAT 25.5% = adequate iron** (validated by ESR 2 / low CRP), no anaemia (Hb 14.8), normal ECG (sinus 63). **Green light to continue the block.** Training-relevant watch-items: **vitamin D 19.92 ng/ml (insufficient)** and **iron not buffered**; CRP 4.6 is consistent with training load (recovery discipline matters).
- **Plan changes applied & mirrored (repo + human + Obsidian, all identical, updated 2026-06-15):** Non-Negotiable Rule 4 (daily D3 1000–2000 IU + iron-aware fuelling); derail #9 cardiac safety-net + #10 supplement insurance; W12 annotated with the indoor-Zwift reality; **W13 Sat 20 Jun upgraded to the outdoor race-kit + nutrition rehearsal** (kept 25–30 km — ACWR 1.46, freshen week).
- **Load/readiness (unchanged from Cycle 11):** ACWR 1.46 (caution; freshen week should drop it) · bike vol 165.5 km/4wk ✓ · adherence ~68% · 4 consecutive easy-run HR breaches (PF re-flare risk) · Imfolozi 12 days out.
- **Dashboard:** re-rendered from cache with the revised plan (render-only; data fresh from 00:11Z sync). No panel changes this cycle.
- **Next:** highest-value action before Imfolozi is the **Sat 20 Jun outdoor nutrition/kit rehearsal** — now the only one left. Hold easy-run HR ≤155 to break the breach streak and protect the foot.


---

## Cycle auto — 2026-06-16

- **Sync at:** 2026-06-16T00:10:17Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 54 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 13 — 2026-06-16 (automated daily · ACWR spike above 1.5 · W13 freshen)

- **⚠️ ACWR 1.58 — crossed the 1.5 injury-risk spike threshold** (build dashboard confirmed). Highest of the block. Acute load driven by Sun Jun 14 Zwift 42.6 km (RE 340) + Mon Jun 15 run (RE 141). W13 is the designed freshen week — volume MUST drop this week or ACWR stays in the red zone into Imfolozi (11 days).
- **5th consecutive easy-run HR breach — Mon 15 Jun:** 5.01 km @ 6:05/km, avg HR **178** vs ≤155 target. Pattern: May 20 (168) · May 27 (182) · May 31 (177) · Jun 8 (180) · Jun 15 (178) — all prescribed Z2 runs, all executed at Z4/LT. No foot pain logged in any of these, but the compounded risk (5-run streak + ACWR 1.58 + active PF) is elevated.
- **Plan gate:** Current (W13 15–21 Jun covers today; plan updated 2026-06-15; no new races). No revision needed.
- **Race readiness (Imfolozi 11d):** 95% (on-track). Bike vol 165/150 km ✓, longest MTB 37/40 km ✓. One gap remains: **outdoor race-kit + nutrition rehearsal (Sat 20 Jun)** — gel/bottle test, race bike, race kit. Non-negotiable.
- **4-week adherence 79%** (15/19 planned sessions). Mid-week quality sessions (Fri tempos, full bike intervals) are the consistent gap; long rides carrying readiness.
- **Amashova (33d): 53% — behind.** Longest road ride 43/90 km; road vol 99/200 km. Phase 4 pivot starts after Imfolozi — must land the 70 km road ride on Sat 4 Jul.
- **Action priority this week:** (1) ACWR must drop — today's Weights (light) fine; Wed bike session = last quality ride, keep HR controlled; Sat 20 Jun outdoor rehearsal = critical but keep to 25–30 km, not 40 km. (2) Easy-run HR ≤155 when running. (3) Daily foot prehab.


---

## Cycle auto — 2026-06-17

- **Sync at:** 2026-06-17T00:09:58Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 54 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-18

- **Sync at:** 2026-06-18T00:09:09Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 54 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-19

- **Sync at:** 2026-06-19T00:09:41Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 55 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-20

- **Sync at:** 2026-06-20T00:08:49Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 55 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 14 — 2026-06-20 (manual · T-7 Imfolozi · ACWR still elevated · outdoor rehearsal day)

- **Plan gate:** Current. W13 (15–21 Jun) covers today; plan updated 2026-06-15; all 4 races reflected; Imfolozi taper (W13) + race week (W14) written. No revision.
- **⚠️ ACWR 1.59 — STILL above 1.5 injury-risk threshold at T-7.** Cycle 13 (Jun 16) expected freshen week to drop it — it hasn't. The acute load remains elevated because Jun 13 Zwift (RE 209) + Jun 14 Zwift (RE 340) + Jun 15 run (RE 141) are still inside the 7-day window. Freshen week mid-sessions (Wed Zwift 119, Thu weights 24) kept acute load high. ACWR was 1.58 on Jun 16; now 1.59 — no meaningful drop. Imfolozi race weekend (Sat 27 Stage 1 + Sun 28 Stage 2) will add further acute load from this already-elevated base.
- **T-7 milestone crossed — Imfolozi race week starts Mon 22 Jun.** Stage 1 (40 km, 07h30 Sat 27) and Stage 2 (15 km, 07h30 Sun 28). Registration Fri 26 Jun 13h00–20h00.
- **W13 adherence so far (5 days):** Mon run ✅ (⚠️ HR 178, 5th consecutive easy-run breach · ≤155 target) · Tue hike instead of weights ⚠️ · Wed Zwift ✅ (HR 147, lower than 170–180 target) · Thu weights ✅ · Fri easy bike ❌ missed.
- **TODAY (Sat 20 Jun) = outdoor race-kit + nutrition rehearsal (25–30 km).** Last opportunity before Imfolozi. Non-negotiable: race bike, race kit, full nutrition (gel at 45 min, bottle every 45 min). CRITICAL: keep to 25–30 km — do not stretch to 40 km with ACWR at 1.59.
- **5th consecutive easy-run HR breach (Jun 15: 178 avg HR):** all prescribed easy runs are being executed at Z4/LT. Pattern unchanged since Cycle 7. No foot pain reported, but PF re-flare risk remains elevated at ACWR 1.59.
- **Action before Imfolozi:** Outdoor rehearsal today (controlled). Tomorrow Sun 21 Jun = 8–10 km easy run (final foot test before Absa 10K — keep HR ≤155, walk if anything twinges). Then race week: Mon easy spin, Tue light weights, Wed openers, Thu rest, Fri registration.
- **Amashova (29d): ~53% — behind.** Phase 4 road pivot starts immediately after Imfolozi. Sat 4 Jul 70 km road ride is the first non-negotiable of Phase 4.


---

## Cycle auto — 2026-06-21

- **Sync at:** 2026-06-21T00:09:24Z
- **Data source:** Strava API
- **Activity baseline:** 6 activities in last 7 days, 55 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 15 — 2026-06-21 (manual · T-6 Imfolozi · outdoor rehearsal confirmed missed · ACWR drops into safe zone)

- **Plan gate:** Current. W13 (15–21 Jun) covers today; plan updated 2026-06-15; Imfolozi taper (W13) + race week (W14) written. No revision.
- **🚨 Sat 20 Jun outdoor race-kit + nutrition rehearsal CONFIRMED MISSED — 3rd consecutive miss.** Actual: Zwift "Watopia's Waistband" 1:15:46, 25.04 km, avg HR 134. Originally scheduled W12 Sat 13 → moved to W13 Sat 20 → missed again. Race nutrition (gel at 45 min, bottle every 45 min, gut test) and race-kit outdoor fit have NOT been rehearsed before Imfolozi (T-6). Highest-risk gap entering race week.
- **ACWR dropped to ~0.82 — back in safe zone.** Jun 14 Zwift RE 340 aged out of the 7-day acute window (acute now ~411 RE). Freshen week worked for load management: ACWR fell from 1.59 (Cycle 14, Jun 20) to the lower-safe-band. This is the intended pre-race state.
- **W13 adherence (6 of 7 days, Sun 21 Jun run still pending):** Mon run ⚠️ HR 178 (5th consecutive easy-run breach ≤155 ceiling) · Tue hike instead of weights ⚠️ · Wed Zwift ✅ (HR 147, below 170–180 target but threshold stimulus) · Thu weights ✅ · Fri easy bike ❌ missed · Sat outdoor rehearsal ❌/⚠️ (Zwift substituted, nutrition not tested).
- **Today (Sun 21 Jun):** prescribed 8–10 km easy run on grass (HR ≤155). Pre-Absa foot test. Not yet logged — will appear in tomorrow's build.
- **Easy-run HR breach streak: 5 consecutive** (May 20: 168 · May 27: 182 · May 31: 177 · Jun 8: 180 · Jun 15: 178). No foot pain reported, but pattern unchanged. Approaching race week: keep W14 easy spins/openers genuinely easy.
- **Imfolozi 6 days — practical note:** outdoor nutrition rehearsal window has closed. Recommend rehearsing nutrition protocol mentally and on the morning warmup spin (Fri 26 Jun openers — 20 min, 2 × 30 sec), accepting the gut-test risk is now race-day managed rather than pre-tested.


---

## Cycle auto — 2026-06-22

- **Sync at:** 2026-06-22T00:09:12Z
- **Data source:** Strava API
- **Activity baseline:** 5 activities in last 7 days, 54 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 16 — 2026-06-22 (manual · W14 IMFOLOZI RACE WEEK starts · Sun foot test confirmed missed)

- **Plan gate:** Current. W14 (22–28 Jun) covers today; plan updated 2026-06-15; taper week + race written. No revision.
- **🏁 RACE WEEK — Imfolozi 55 km MTB in 5 days.** Stage 1 Sat 27 Jun 40 km · Stage 2 Sun 28 Jun 15 km. Registration Fri 26 Jun 13h00–20h00. W14 plan: Mon easy spin/rest · Tue light weights · Wed 45 min easy + 3 × 1 min openers · Thu rest + pack · Fri travel + registration + 20 min easy spin.
- **Sun 21 Jun foot test run CONFIRMED MISSED** (pending in Cycle 15, now confirmed by fresh build — 0 runs in last 7 days). Pre-Absa 10K foot assessment not executed. **Consequence: Absa 10K strategy (1:02–1:05 vs 1:08 finish) cannot be decided until the first easy run in W15 (Wed 2 Jul)** — that becomes the new foot-test session.
- **ACWR ~0.72 — planned taper state.** Jun 14 Zwift (RE 340) aged out of the acute window; freshen week worked for load management. This is the intended race-week state: body freshen, no new load until race day.
- **Outdoor race-kit + nutrition rehearsal: never done (3 missed opportunities).** Accepted risk per Cycle 15 — gut-test is now race-day managed. Mental rehearsal recommended on the Fri 26 Jun warmup spin.
- **Easy-run HR breach streak: 5 consecutive** (through Jun 15). No run logged since Jun 15. Pattern paused by freshen week; enforce HR ≤155 strictly on W15 recovery runs.
- **Race-week priorities:** (1) Rest and hydrate — no extra sessions. (2) Pack race kit + nutrition plan before Thu. (3) Fri 26 registration + 20 min easy spin + 2 × 30 sec openers. (4) Sat 27 Stage 1: RPE 6–7, conversational first 2/3, save legs for Sunday. (5) Post-race: first easy run in W15 = foot test + ACWR reset.


---

## Cycle auto — 2026-06-23

- **Sync at:** 2026-06-23T00:09:15Z
- **Data source:** Strava API
- **Activity baseline:** 5 activities in last 7 days, 54 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 17 — 2026-06-23 (manual · T-4 Imfolozi · race-week protocol breach)

- **Plan gate:** Current. W14 (22–28 Jun) covers today; plan updated 2026-06-15; race week fully written. No revision.
- **🚨 Race-week protocol breach — Mon Jun 22:** W14 plan = "Easy 30 min spin OR rest". Actual = **10.03 km run @ 6:21/km, avg HR 174, RE 289** — threshold-intensity 10 km run 4 days before Imfolozi Stage 1. This is the 6th consecutive easy-prescribed run above the ≤155 HR ceiling (streak: May 20 168 · May 27 182 · May 31 177 · Jun 8 180 · Jun 15 178 · Jun 22 174). Appeared to serve as the delayed Sun 21 Jun foot-test run (Sun was missed), but intensity was wrong for race week. Legs may carry residual fatigue into race day.
- **ACWR 0.88** — safe zone, up from the 0.72 taper state (Jun 22 RE 289 re-entered the 7-day acute window). No spike, but load is higher than the intended pre-race state.
- **Foot:** 10 km at 6:21/km completed without logged pain → foot is tolerating race-ready distances. But no explicit pain-status update in injury log since 27 May.
- **Imfolozi T-4:** Stage 1 Sat 27 Jun 40 km / 07h30, Stage 2 Sun 28 Jun 15 km / 07h30. Registration Fri 26 Jun 13h00–20h00. Remaining W14: Tue 23 light weights; Wed 24 easy 45 min + 3×1 min openers; Thu 25 rest + pack; Fri 26 travel + registration + easy spin. **No more quality sessions before race day.**
- **Race-week directives:** (1) No additional runs before race day. (2) Wed openers = genuinely easy — HR ≤155, 3 brief pickups only. (3) Hydrate hard Thu–Fri. (4) Nutrition plan: mental rehearsal since outdoor test never happened — gel at 45 min, bottle every 45 min, no surprises.


---

## Cycle auto — 2026-06-24

- **Sync at:** 2026-06-24T00:09:34Z
- **Data source:** Strava API
- **Activity baseline:** 4 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-25

- **Sync at:** 2026-06-25T00:09:09Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-06-26

- **Sync at:** 2026-06-26T00:09:27Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle 18 — 2026-06-26 (manual · RACE EVE — Imfolozi Stage 1 TOMORROW)

- **Plan gate:** Current. W14 (22–28 Jun) covers today; plan updated 2026-06-15; taper + race week written. No revision.
- **🏁 MILESTONE: Imfolozi 55 km MTB race eve.** Stage 1 (40 km, 07h30 Sat 27 Jun) in ~7 hours. Stage 2 (15 km, 07h30 Sun 28 Jun) the following morning. Registration today 13h00–20h00 at race village.
- **ACWR 0.66 — appropriate taper.** (7-day RE 385: Jun 20 Zwift 96 + Jun 22 run 289; 28-day avg 83.1 RE/day.) Taper worked — ACWR fell from the 1.59 caution peak (Cycle 14, Jun 20) to well below the safe-band lower bound. Body is freshen-ready for race day.
- **W14 adherence (Mon–Fri): 1/4.** Mon 22: 10 km run HR 174 (plan = easy spin/rest — 6th consecutive easy-run HR breach). Tue 23, Wed 24: nothing logged (weights + easy openers both missed). Thu 25: rest ✓. The unlogged Wed openers session is low-risk to skip — legs fresher for race day without it.
- **Outstanding risk — outdoor nutrition rehearsal: 3 missed, never executed.** Gel-at-45-min / bottle-every-45-min protocol goes into Imfolozi untested on trail. Race-day managed: rehearse mentally on the Fri evening warmup spin tonight; stick to the plan, no improvisation on course.
- **Foot: holding.** Jun 22 10 km run (6:21/km) completed without logged pain — last formal injury-log entry was May 27 (90% better). No acute deterioration. Continue prehab tonight.
- **Post-race priorities:** Mon 29 Jun = full rest. First W15 easy run (Wed 2 Jul) = foot reassessment + ACWR reset. Immediate pivot to road cycling for Amashova (23 days, Phase 4).


---

## Cycle auto — 2026-06-27

- **Sync at:** 2026-06-27T00:09:01Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 19 — 2026-06-27 (manual · IMFOLOZI RACE DAY — Stage 1)

- **🏁 MILESTONE: Imfolozi 55 km MTB — Stage 1 today (40 km, 07h30), Stage 2 tomorrow (15 km, 07h30).** This is the A-race the entire May–Jun block was built around.
- **ACWR 0.58** — taper complete, below safe-band floor by design. Body is freshen-ready. Post-race (both stages combined RE ~400-500 est.) ACWR will rebound to ~0.8-1.0.
- **Bike vol 4wk: 165.6 km ✓** (target 150 km met). Longest MTB 36.86 km (Jun 6). Volume readiness green.
- **Outstanding gap going in:** outdoor nutrition rehearsal never executed (3 missed opportunities — all done on Zwift). Gel-at-45-min / bottle-every-45-min untested on trail. Race-day managed; stick to the plan.
- **Foot: holding.** Jun 22 10 km run (6:21/km, HR 174) completed without pain — no new injury-log entry since May 27 ("90% better"). Continue prehab tonight and tomorrow morning.
- **Easy-run HR breach streak: 6 consecutive** — not actionable race day; flag for W15 recovery runs (enforce ≤155).
- **Post-race log:** Stage 1 result should appear in tomorrow's build. If Stage 2 (Sun 28) syncs, W14 will be complete. Next manual cycle after results land.
- **Phase pivot:** immediately after Imfolozi → road cycling for Amashova (22 days, Sun 19 Jul). Sat 4 Jul 70 km road ride is the first non-negotiable of Phase 4.


---

## Cycle auto — 2026-06-28

- **Sync at:** 2026-06-28T00:12:35Z
- **Data source:** cached (Strava unreachable)
- **Activity baseline:** 1 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 20 — 2026-06-28 (manual · IMFOLOZI STAGE 2 RACE DAY · Phase 4 pivot)

- **🏁 MILESTONE: Imfolozi 55 km MTB — Stage 2 today (15 km, 07h30).** W14 A-race block concludes today. Stage 1 result (Sat 27 Jun, 40 km) and Stage 2 (today) not yet in Strava cache — sync was 28+ hours stale (last-sync: 2026-06-27T00:09:01Z). Results should appear in tomorrow's automated build.
- **Dashboard bug patched:** `render_races()` raised `KeyError: 'past'` when a race's `status_cls` was `'past'` (Imfolozi Stage 1 now past its start date). Fixed: `.get(status_cls, "currentColor")` fallback. Dashboard rendered successfully on cached data.
- **ACWR 0.58 (stale/taper):** Pre-race base; Imfolozi stages (est. RE 200–350 each) not in data yet. Post-sync ACWR expected to rebound to ~0.8–1.0 (safe zone).
- **Easy-run HR breach streak: 6 consecutive** (May 20–Jun 22, range 168–182 vs ≤155 ceiling). No foot pain reported. First W15 easy run (Wed Jul 2) is the PF foot-test and must enforce ≤155.
- **Phase 4 pivot (Amashova road build) starts Mon 29 Jun:** Road vol = 0/200 km. Non-negotiables — Sat 4 Jul: 70 km road ride · Fri 10 Jul: Absa 10K easy (≤1:10, do NOT race) · Sun 12 Jul: 85–90 km road ride. Amashova is 21 days away.


---

## Cycle auto — 2026-06-29

- **Sync at:** 2026-06-29T00:09:59Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 53 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 21 — 2026-06-29 (manual · IMFOLOZI COMPLETE · Phase 4 pivot · ACWR spike)

- **🏆 MILESTONE: Imfolozi 55 km MTB COMPLETED.** Stage 1 Sat 27 Jun: 40.6 km / 3:08 / avg HR 163 / 941m elevation. Stage 2 Sun 28 Jun: 11.9 km / 48 min / avg HR 147 (slightly shorter than planned 15 km — likely course variation). The entire May–Jun block was built around this race; it landed. Foot held across both stages.
- **⚠️ ACWR 1.63 — above the 1.5 injury-risk spike threshold.** Acute 7-day RE = 1080 (run 289 + Stage 1 684 + Stage 2 107). Chronic weekly avg = 664 RE. This spike is expected post-A-race but elevated given active PF recovery. Today is W15 Day 1 (planned Rest) — ACWR will drop naturally through the recovery week. No additional load before Wed 2 Jul easy run.
- **Easy-run HR breach streak: 6 consecutive** (May 20: 168 · May 27: 182 · May 31: 177 · Jun 8: 180 · Jun 15: 178 · Jun 22: 174). All prescribed Z2 runs executed at Z4/LT. Foot has held without logged pain, but this pattern must be addressed in W15+ — enforce HR ≤155 ceiling, especially on the Wed 2 Jul foot-test run.
- **Phase 4 pivot (Amashova road build) starts today (W15):** Road vol = 0/200 km target. Amashova (106 km road cycling) is 20 days away. Non-negotiables: Sat 4 Jul 70 km road ride · Fri 10 Jul Absa 10K easy (do not race) · Sun 12 Jul 85–90 km road ride.
- **Plan updated:** Imfolozi checkboxes marked complete; `updated:` bumped to 2026-06-29. Plan-history entry appended. Obsidian mirror needs manual sync.


---

## Cycle auto — 2026-06-30

- **Sync at:** 2026-06-30T00:11:27Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 52 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-01

- **Sync at:** 2026-07-01T00:10:37Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 51 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-02

- **Sync at:** 2026-07-02T00:10:41Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 50 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 22 — 2026-07-02 (manual · post-Imfolozi ACWR recovery · Phase 4 Day 4)

- **Plan gate:** Current. W15 (29 Jun–5 Jul) covers today (Thu); plan updated 2026-06-29; all races reflected; no triggers fired.
- **ACWR ~1.22 — back in safe zone (0.8–1.3).** Recovered from the post-Imfolozi spike of 1.63 (Cycle 21, Jun 29) via 4 rest/recovery days. Acute (last 7d) = Stage 1 RE 684 + Stage 2 RE 107 = 791; chronic weekly avg = 648. Recovery working.
- **W15 (Jun 29–Jul 2 so far):** Mon Rest ✓ · Tue weights + Wed easy run not logged in Strava (either unlogged or not yet done) · Thu weights today (pending). No post-race foot pain reported across Imfolozi stages.
- **⚠️ CRITICAL — Sat 4 Jul 70 km road ride is 2 days away.** First road ride for Amashova (17 days). Road vol = 0/200 km. Skipping this would make a first-time 90 km road rehearsal (Sun 12 Jul) an even greater leap. Non-negotiable.
- **Injury log stale since 2026-05-27 (36 days).** Last entry: 90% PF recovery. Foot held across both Imfolozi stages (10 km run Jun 22 + 40.6 km MTB Jun 27 + 11.9 km MTB Jun 28, no logged pain). Recommend updating injury log with post-Imfolozi status (manual only — cannot reach Obsidian from here).
- **Upcoming:** Sat 4 Jul 70 km road ride · Fri 10 Jul Absa 10K easy (≤1:10, do NOT race) · Sun 12 Jul 85–90 km road ride dress rehearsal · Sun 19 Jul Amashova 106 km.


---

## Cycle auto — 2026-07-03

- **Sync at:** 2026-07-03T00:11:10Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 48 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 23 — 2026-07-03 (manual · Phase 4 Day 5 · Amashova gap quantified · foot test pending)

- **Plan gate:** Current. W15 (29 Jun–5 Jul) covers today (Fri); plan updated 2026-06-29; no triggers fired.
- **ACWR 1.22 — safe zone.** Recovered from post-Imfolozi spike of 1.63 (Jun 29) via rest week. No spike concern.
- **4-week adherence: 54% (13/24).** Post-race recovery week depressed the count — weights unlogged in Strava, Wed foot test run missed. Imfolozi stages carried the block's load.
- **⚠️ Wed Jul 1 easy run CONFIRMED MISSED — first post-Imfolozi foot test not executed.** No run logged since Jun 22. Absa 10K is Fri Jul 10 (7 days). Need at least one easy run (HR ≤155) before race day. Today is road bike, Sat is 70 km road ride, Sun 5 Jul = first run window.
- **⚠️ Amashova (16d): 59% — behind.** Longest road ride 43/90 km; road vol 4wk 129/200 km. **Sat 4 Jul 70 km road ride (tomorrow) is non-negotiable** — first real road ride of Phase 4. Missing it would mean the first 70 km+ road attempt is race week.
- **Foot: stable.** Dashboard: "Resolving, ~90% recovered." No pain logged across both Imfolozi stages or since. Injury log last updated 27 May — post-Imfolozi status update needed (manual/Obsidian only).


---

## Cycle auto — 2026-07-04

- **Sync at:** 2026-07-04T00:09:29Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 48 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-05

- **Sync at:** 2026-07-05T00:09:48Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 48 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 24 — 2026-07-05 (manual · Phase 4 Day 7 · Amashova critical gap)

- **Plan gate:** Current. W15 (29 Jun–5 Jul) covers today; plan updated 2026-06-29; all races reflected. No triggers fired.
- **ACWR: 0.18 — post-race trough.** Acute 7d RE = 107 (Stage 2 only; Stage 1 aged out). Chronic weekly avg = 590. Expected post-A-race, but the trough is now 7 days deep — resumes urgent.
- **🚨 Sat 4 Jul 70 km road ride NOT LOGGED — Phase 4 non-negotiable missed.** Zero road/outdoor bike rides since Imfolozi. All 28d bike km are Zwift. With Amashova in 14 days (Sun 19 Jul), the first outdoor road ride still hasn't happened. Remaining window: today (easy run or rest) → Mon 6 Jul easy run → Tue light weights → **Wed 8 Jul bike intervals (last hard session before Absa)** → Thu rest → Fri Absa 10K → Sat/Sun: 85–90 km road ride is the dress rehearsal (was planned Jul 12 as the big one — the Jul 4 ride was supposed to be the easier 70 km lead-in). With Jul 4 missed, the Jul 12 90 km ride is now a first-ever outdoor road ride at that distance — risk elevated.
- **4-week adherence: ~46%** (Jun 7–Jul 5). Imfolozi stages carried the block; W15 is near-zero (1/7 = 14%). Weights + easy runs all unlogged in Strava this week.
- **Foot: holding.** No pain logged across Imfolozi stages. Last run Jun 22 (10 km @ 6:21/km, HR 174 — hard, not easy). **Post-race foot test run still not done (13 days since last run).** Absa 10K is Fri Jul 10 — needs at least 1 easy run before. Today's plan says "Easy 30 min run or rest" — this should be the foot test.
- **Easy-run HR breach streak: 6 consecutive** (through Jun 22 — all ≥174 avg vs ≤155 ceiling). Streak technically paused by recovery (no runs). Must enforce ≤155 when running resumes — foot still resolving, PF re-flare risk persists.
- **Race countdown:** Absa 10K 5d · Amashova 14d · Hollywoodbets 56d.
- **Action priority:** (1) Today — easy 30 min run as foot test, HR ≤155 strict. (2) Mon 6 Jul — easy run 4 km. (3) Wed 8 Jul — bike intervals per plan. (4) **Sat 12 Jul — 85–90 km outdoor road ride is now the ONLY long road ride before Amashova.** Do not miss it. Nutrition and kit rehearsal must happen on that ride.


---

## Cycle auto — 2026-07-06

- **Sync at:** 2026-07-06T00:14:17Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 48 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 25 — 2026-07-06 (automated daily · plan revised · ACWR trough · W16 start)

- **Plan revision (trigger e):** Sat 4 Jul 70 km road ride confirmed missed — no activities logged Jun 29–Jul 5 (full W15 rest). Plan annotated with missed check-in and Week 16 warning block. Injury log updated: foot status upgraded from "Resolving ~90%" to "Effectively resolved" following Imfolozi completion (0/10 pain both stages). `plans/training-plan.md updated: 2026-07-06`.
- **ACWR ≈ 0.0** — Stage 2 Jun 28 (RE 107) aged out of the 7-day window today. Acute = 0; chronic avg = 590/wk. ACWR has collapsed from the post-Imfolozi spike of 1.63 (Jun 29) to a full trough. Lowest of the block. Not injury risk, but undertraining risk with Amashova 13 days away. Today's Mon easy run (4 km, HR ≤155) is the reset.
- **4-week adherence ~46%;** W15 near-zero (0 logged sessions). Imfolozi A-race carried the block. The 6-consecutive easy-run HR breach streak (May 20–Jun 22, all ≥174 vs ≤155) is technically paused — must enforce ≤155 when running resumes or the PF re-flare risk re-opens.
- **Critical path to Amashova (13d):** Mon easy run → Wed 8 Jul bike intervals (last hard session) → Thu rest → Fri Absa 10K easy C-race (≤1:10, do NOT race) → Sat easy spin → **Sun 12 Jul 85–90 km outdoor road ride (non-negotiable — the ONLY long road ride before Amashova)**. Nutrition + kit dress rehearsal must happen on the Sunday ride.
- **Race countdown:** Absa 10K 4d · Amashova 13d · Hollywoodbets 55d. Foot: resolved.


---

## Cycle auto — 2026-07-07

- **Sync at:** 2026-07-07T00:10:00Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 48 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-08

- **Sync at:** 2026-07-08T00:09:51Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 47 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-09

- **Sync at:** 2026-07-09T00:10:04Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 46 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 26 — 2026-07-09 (automated daily · ABSA 10K EVE · Amashova T-10 · Wed intervals missed)

- **Plan gate:** Current. W16 (6–12 Jul) covers today; plan updated 2026-07-06; all races reflected; Absa has Thu rest + easy-effort Friday covered. No revision.
- **🏃 ABSA 10K TOMORROW (Fri 10 Jul, C race tune-up).** Easy effort target: ≤1:10, HR ≤160. Do NOT race. Last run: Jun 22 (17 days ago). Foot resolved (0/10 across both Imfolozi stages). Today is prescribed rest — hold it.
- **⚠️ Wed 8 Jul bike intervals CONFIRMED MISSED.** 5×5 min @ HR 165–175 not executed. Means Amashova going in with zero road cycling quality sessions since Imfolozi (Jun 28) and ACWR ≈ 0. No mid-week cardio logged this week at all (Mon = walk only).
- **ACWR ≈ 0 — full trough.** Acute 7-day RE ≈ 0 (Jul 6 walk, RE=0); chronic weekly avg ≈ 550. Undertraining risk, not injury risk — but the jump to Sun 12 Jul 85–90 km road ride (3 days away) will be significant.
- **🚨 Sun 12 Jul 85–90 km outdoor road ride is 3 days away and NON-NEGOTIABLE.** It is the ONLY long road ride before Amashova (T-10). Race kit + full nutrition dress rehearsal must happen on this ride. Skipping or shortcutting it would mean a first-ever 106 km road ride is Amashova race day.
- **Foot: 0/10, resolved.** Continue daily prehab. Enforce HR ≤160 during Absa.


---

## Cycle auto — 2026-07-10

- **Sync at:** 2026-07-10T00:10:31Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 45 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-11

- **Sync at:** 2026-07-11T00:10:43Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 44 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 27 — 2026-07-11 (automated daily · Absa 10K outcome unknown · ACWR trough · Amashova T-8)

- **Plan revision (trigger a):** Absa 10K (Fri 10 Jul) still in Active Races. Moved to Past with result "pending Strava upload" — no activity in Strava as of 11 Jul sync (44 activities, down from 45). Checklist item flagged `[?]`. Plan + race-calendar `updated: 2026-07-11`. **Obsidian local mirror needs manual sync.**
- **⚠️ Absa 10K outcome unknown.** No Strava activity for Jul 10. Either the race was not run, or it was run and not yet uploaded. If Theo ran it: upload the Garmin activity to Strava and the next build will capture the result. If skipped: note in the injury log and plan checklist.
- **ACWR 0.00 — full detraining trough** (7-day acute RE = 0 from Mon Jul 6 walk RE=0; chronic avg ~550/wk). Not injury risk but the sudden jump to tomorrow's 85–90 km road ride will be significant. Execute at RPE 5–6 (HR ≤155), eat + drink on schedule — legs will be undertrained.
- **4-week adherence 35% (8/23)** — depressed by W15 full recovery + W16 low logging. Only logged session this week: Jul 6 morning walk.
- **🚨 TOMORROW Sun 12 Jul = 85–90 km outdoor road ride — non-negotiable.** The ONLY long road ride before Amashova (T-8). Nutrition + kit dress rehearsal must happen on this ride. Missing it means a first-ever 106 km road ride would be Amashova race day. This is the highest-priority session left in Phase 4.
- **Amashova (T-8): 50% readiness (behind).** Longest road ride 43/90 km; road vol 4wk 89/200 km. If Sun 12 Jul lands at 85–90 km, readiness will jump significantly.
- **Foot: 0/10, effectively resolved.** Daily prehab continues.


---

## Cycle auto — 2026-07-12

- **Sync at:** 2026-07-12T00:10:39Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 44 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-13

- **Sync at:** 2026-07-13T00:31:57Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 44 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 28 — 2026-07-13 (automated daily · AMASHOVA T-6 · critical prep gap confirmed)

- **🚨 AMASHOVA DRESS REHEARSAL CONFIRMED MISSED — T-6.** Sun 12 Jul 85–90 km outdoor road ride (the last non-negotiable before Amashova 106 km on Jul 19) has 0 Strava activity as of 00:31 UTC Jul 13. This was the ONLY long road ride planned for Phase 4 after the Sat 4 Jul 70 km was also missed. Longest outdoor road ride on record: 39.35 km (Apr 19, pre-PF). Going into a 106 km race with no outdoor road rides since Jan–Mar (pre-plan period).
- **ACWR 0.0 — absolute trough.** Acute 7-day RE ≈ 0 (Jul 6 walk, RE=0; Jul 7–12 nothing). Chronic 28-day avg ≈ 53 RE/day. Not injury risk but undertraining for a 106 km race. Last meaningful training was Imfolozi Stage 2 (Jun 28, RE 107) — 15 days ago.
- **Plan vs actual last 7 days:** 0/5 key sessions completed (Jul 6 walk substituted for run; Jul 7 weights ❌; Jul 8 bike intervals ❌; Jul 10 Absa 10K ❌/⚠️ unknown; Jul 11 easy spin ❌; Jul 12 85–90 km road ❌).
- **Absa 10K (Jul 10) outcome still unknown.** No Strava upload as of this sync. Either not run or not uploaded. This will determine whether there's at least one recent cardio session on record.
- **4-week adherence ~35%** (last 4 weeks, Jun 15–Jul 12): only the two Imfolozi race stages and scattered mid-week sessions logged. W16 = 0 key sessions.
- **Amashova (T-6) race strategy revised:** Completion-only goal. Pacing target: HR ≤145 first 50 km (strict — will feel embarrassingly easy), eat every 30 min from first 30 min, drink 1 bottle/hr minimum, accept 5 hr+ finish. The risk is blowing up in the second half at an underprepared aerobic base. The body hasn't done this distance or anything close.
- **Foot: 0/10 (resolved).** Daily prehab continues.
- **Plan revision:** Plan checklist updated — Sun 12 Jul marked ⚠️ MISSED. Plan-history.md entry added.
- **Note:** Obsidian local mirror of plan needs manual sync.


---

## Cycle auto — 2026-07-14

- **Sync at:** 2026-07-14T00:10:33Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-15

- **Sync at:** 2026-07-15T00:11:44Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-16

- **Sync at:** 2026-07-16T00:12:40Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-17

- **Sync at:** 2026-07-17T00:10:45Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 44 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 29 — 2026-07-17 (manual · AMASHOVA T-2 · race-week REST breach)

- **Plan gate:** Current. W17 (13–19 Jul, Amashova race week) covers today (Fri); plan updated 2026-07-13; no triggers fired.
- **⚠️ Race-week REST breach — Thu 16 Jul:** W17 plan = Rest. Actual = **7.05 km run / 57:05 / avg HR 161 / RE 193**. This is the day before race-eve (Sat rest + travel). HR 161 exceeds the easy-run ≤155 ceiling; pace 8:06/km suggests genuinely easy effort despite the HR overshoot, but adding 57 min of running legs the day before an undertrained 106 km cycle is not ideal.
- **T-2 context:** Going into Amashova with 0 outdoor road rides (longest outdoor road ride = 39 km on Apr 19), ACWR ≈ 0.28 (acute 7 km / chronic 25 km/wk by distance), and 0/3 key Phase 4 non-negotiables completed (Jul 4 70 km ❌, Absa 10K ❌ no upload, Jul 12 85–90 km ❌). Race strategy from Cycle 28 stands: completion-only, HR ≤145 first 50 km, eat every 30 min, accept 5+ hr finish.
- **4-week adherence ~35%** (W14–17). Imfolozi stages carried the last meaningful load.
- **Foot: 0/10, resolved.** Daily prehab continues.
- **Action for race day (Sun 19 Jul):** Hold HR ≤145 for first 50 km — this is the single most important determinant of finishing vs blowing up. Do not chase groups. Eat and drink on schedule regardless of feel. Walk any sustained climb in the second half if HR rises above 155.


---

## Cycle auto — 2026-07-18

- **Sync at:** 2026-07-18T00:11:35Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 44 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 30 — 2026-07-18 (AMASHOVA EVE · race-eve run breach · ACWR spike)

- **Plan gate:** Current. W17 (13–19 Jul) covers today; plan updated 2026-07-13; taper + race written; injury log (Jul 6) older than plan. No revision.
- **🚨 RACE-EVE RUN BREACH — Fri 17 Jul:** Plan = "30 min easy spin + openers (pack collection at expo)". Actual = **6.2 km run / 48:25 / avg HR 169 / RE 191**. Third consecutive race-week run instead of prescribed rest or easy spin (Mon 13 missing spin, Thu 16 REST breach 7.05 km HR 161, Fri 17 race-eve run HR 169). This is the 8th overall easy-run HR breach (≤155 ceiling).
- **ACWR 1.30 — jumped to top of safe band** (acute 7d RE 520: Tue weights 136 + Thu run 193 + Fri run 191; chronic 4wk avg 400/wk). Entered the week at ~0. ACWR spike from two back-to-back runs in the final 48 hr before a 106 km race is non-ideal but technically within the safe zone (0.8–1.3).
- **4-week adherence ~35%** — W14–17. Only 3 sessions this week (Tue weights ✓; Thu–Fri runs = plan breaches, not planned sessions). Mon spin ❌ missed, Wed bike openers ❌ missed.
- **AMASHOVA (Sun 19 Jul) RACE STRATEGY (unchanged from Cycle 28):** Completion-only. HR ≤145 first 50 km — non-negotiable, set Garmin alarm. Eat every 30 min from km 30, 1 bottle/hr. No outdoor road rides completed in Phase 4; longest outdoor road ride = 39 km (Apr 19). Accept 5+ hr finish; blowing up in the second half is the primary risk.
- **Foot: 0/10 (resolved).** Daily prehab continues.
- **Next cycle:** Amashova result will appear in Monday's automated build. Manual review post-race to pivot Phase 5 (Hollywoodbets sub-60 run build, 42 days, Aug 30).


---

## Cycle auto — 2026-07-19

- **Sync at:** 2026-07-19T00:09:43Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-20

- **Sync at:** 2026-07-20T00:14:38Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 31 — 2026-07-20 (Phase 5 start · Amashova result unknown · ACWR spike 1.59)

- **Phase transition:** Phase 5 (Hollywoodbets Sub-60 Run Build) begins today. W18 Day 1 = planned Rest (Mon 20 Jul). Hollywoodbets 10K is 41 days away.
- **🚨 ACWR spike: 1.59 (above 1.5 injury-risk threshold).** Acute 7d RE = 520 (weights 136 + Thu run 193 + Fri run 191). Chronic 4wk avg dropped to 327.8 today because the Jun 22 long run (RE 289) aged out of the 28-day window. Yesterday ACWR was 1.30 (within safe band); today it crossed the 1.5 ceiling. Particularly significant given PF history — run ramp in Phase 5 must be gradual (HR ≤155, max 4-6 km for first easy runs this week).
- **Amashova result: STILL MISSING after fresh sync (2026-07-20T00:14:38Z, 43 activities unchanged).** Race occurred Sun 19 Jul; sync is now ~14 hr post-race and no activity uploaded. Either not yet uploaded (likely — athlete rest/fatigue) or race not completed. Check tomorrow's auto-build. If completed, ACWR will spike further on upload (a 106 km race RE ~600–800 would push ACWR to ~3.0+).
- **Phase 5 ramp guidance (critical given current ACWR):** Do NOT start run sessions until ACWR drops back toward 1.0. Mon–Tue = rest only. Wed 22 Jul easy run 4 km = absolute maximum. Enforce HR ≤155 ceiling from day 1. This week's plan (W18) is appropriately conservative — follow it exactly.
- **Foot: 0/10.** Effectively resolved; daily prehab continues. Monitor first runs of Phase 5.
- **Obsidian mirror:** plan updated 2026-07-20; manual sync needed.


---

## Cycle auto — 2026-07-21

- **Sync at:** 2026-07-21T00:12:35Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 42 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 32 — 2026-07-21 (manual · ACWR resolves · Amashova still missing 48hr post-race)

- **ACWR 1.17 — returned to safe zone.** Yesterday's 1.59 spike (Cycle 31) was driven by Jul 14 Weights (RE 136) inside the 7-day acute window; today it aged out, dropping acute from 520→384 (Jul 16 run RE 193 + Jul 17 run RE 191). Chronic 4wk avg ≈ 328. Phase 5 run ramp must stay gradual — first runs this week should cap at 4 km, HR ≤155.
- **🚨 Amashova result: 48hr post-race, still no Strava upload (42 activities, unchanged from yesterday).** Race occurred Sun 19 Jul. Either not yet uploaded (manual upload from Garmin/Wahoo pending) or race was not completed. When it uploads, expect ACWR to jump to 2.5–3.5+ (a 106 km race RE ~600–800); if that happens, delay W18 runs until ACWR drops below 1.3.
- **Phase 5 start (Hollywoodbets 10K, Aug 30, 40 days):** W18 today (Tue 21) = Easy 30 min spin OR walk. Plan is correct — no deviation needed. Sub-60 interval sessions don't begin until W20 (5 Aug). Today: active recovery only.
- **Foot: 0/10.** Daily prehab continues. No change since Imfolozi.


---

## Cycle auto — 2026-07-22

- **Sync at:** 2026-07-22T00:12:46Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 42 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 33 — 2026-07-22 (manual · Amashova Day 3 no upload · ACWR 1.25 · Phase 5 W18)

- **🚨 Amashova Day 3 — still no Strava upload (72hr post-race, 42 activities unchanged).** Jul 19 race not in Strava after 3 syncs (Jul 20, Jul 21, Jul 22). At this lag, either Garmin/Wahoo upload is pending (manual action needed) or race was not completed (DNF). When it uploads, expect ACWR spike to 2.5–3.5+ — delay Phase 5 runs until ACWR drops back below 1.3 if that happens.
- **ACWR 1.25** — safe zone. Acute 7d RE = 419 (Jul 16 run 193 + Jul 17 run 191 + Jul 21 weights 35); chronic 28d avg 336.5/wk. Slight uptick from yesterday's 1.17 as Tue weights entered the acute window. Still safe; no spike.
- **Phase 5 W18 (20–26 Jul):** Mon REST ✓ · Tue weights 56:46 ✓ (logged fresh this sync). Today (Wed 22) = easy run 4 km, HR ≤155 — first planned run of Phase 5. Enforce HR ceiling — 8-consecutive easy-run breach streak on record.
- **Hollywoodbets 10K: 39 days (Aug 30). Foot: 0/10.** Sub-60 interval sessions begin W20 (5 Aug). Plan current, no revision needed.


---

## Cycle auto — 2026-07-23

- **Sync at:** 2026-07-23T00:14:55Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 41 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 34 — 2026-07-23 (automated daily · plan revision · ACWR drops · Phase 5 W18 D4)

- **Plan revision (trigger e):** Amashova (Jul 19) still in Active Races 4 days post-race. Moved to Past in `race-calendar.md` with result "not on Strava as of 96hr post-race." Plan checklist item updated to reflect 96hr+ no upload. `updated:` → 2026-07-23.
- **🚨 Amashova — 96hr post-race, still no upload (41 activities).** Fifth consecutive sync with no Jul 19 activity. Action needed: manual Garmin/Wahoo upload to Strava. If race not completed, note DNF in plan checklist.
- **ACWR 0.67 — below safe band floor (0.8).** Jul 16 run (RE 193) aged out today; acute = 226 (Jul 17 run + Jul 21 weights); chronic avg ≈ 337/wk. Undertraining zone — Phase 5 run ramp must start now. If Amashova uploads with RE ~600-800, ACWR will spike to 2.5-3.5+ and W18 runs must pause until it drops below 1.3.
- **4-week adherence 24% (5/21).** Depressed by W15-W16 rest and W17 race breaches. W18 on track: Mon REST ✓ · Tue Weights 56:46 ✓ · Wed run pending next sync · Thu today = weights light.
- **Hollywoodbets (38d): 39%, at-risk.** Run vol 4wk 13/30 km; fastest pace 4wk 7:48/km (target 5:59); no interval sessions yet. Sub-60 build needs to accelerate. Critical: W20 (Aug 5) 5×800m @ 5:30/km, W21 (Aug 12) 4×1km @ 5:55/km.


---

## Cycle auto — 2026-07-24

- **Sync at:** 2026-07-24T00:12:51Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 42 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-25

- **Sync at:** 2026-07-25T00:13:05Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 42 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-26

- **Sync at:** 2026-07-26T00:10:45Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 42 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 35 — 2026-07-26 (manual · W18 last day · ACWR trough · Phase 5 run debt)

- **Plan gate:** Current. W18 (20–26 Jul) covers today (Sun); plan `updated: 2026-07-23`; injury log (Jul 6) older than plan; Hollywoodbets only active race (Aug 30). No triggers fired.
- **ACWR 0.45 — below safe-band floor (0.8).** Acute 7d RE = 80 (Tue weights 35 + Thu weights 45); chronic 28d avg ≈ 177/wk. Significant trough — not injury risk, but detraining concern with Hollywoodbets 35 days out. Phase 5 run base must start immediately in W19.
- **W18 plan vs actual:** Mon REST ✓ · Tue Weights 56:46 ✓ (plan: spin/walk) · Wed easy run 4 km ❌ MISSED · Thu Weights 1:11 ✓ · Fri easy run 5 km ❌ MISSED · Sat REST ✓ · Sun today (easy run 6 km, not yet logged). Last run was Jul 17 (9 days ago). Two consecutive planned runs skipped — first Phase 5 run week was essentially bike-only.
- **🚨 Amashova: 7 days post-race, still no Strava upload (42 activities unchanged).** Either manual upload pending or DNF. If uploaded, ACWR will spike to 2.5–3.5+; delay W19 runs until ACWR drops below 1.3. Manual action needed — check Garmin/Wahoo app and upload.
- **Hollywoodbets (35d): at-risk.** Run vol 4wk ≈13 km vs 30 km target; fastest recent pace 7:48/km vs 5:59/km race target; zero interval sessions completed. W20 (Aug 5) 5×800m @ 5:30/km is the first sub-60 session — 10 days away with essentially no run base under it.
- **Foot: 0/10, resolved.** Daily prehab continues. No new entries since Jun 28.
- **W19 priority (starts tomorrow):** Mon easy run 6 km (HR ≤155) is the reset — must happen. Wed strides + form, Sat long run 10 km. The sub-60 build cannot afford another low-run week.


---

## Cycle auto — 2026-07-27

- **Sync at:** 2026-07-27T00:16:20Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 43 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-28

- **Sync at:** 2026-07-28T00:18:41Z
- **Data source:** Strava API
- **Activity baseline:** 3 activities in last 7 days, 41 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 36 — 2026-07-28 (automated daily · ACWR recovery 0.45→1.04 · HR breach flag · W19 Day 2)

- **Plan gate:** Current. W19 (27 Jul–2 Aug) covers today; plan `updated: 2026-07-23`; injury log (Jul 6) older than plan; Hollywoodbets only active race (Aug 30, 33 days). No triggers fired.
- **ACWR 1.04 — back in optimal band (0.8–1.3).** Recovery from 0.45 trough (Cycle 35 Jul 26). Acute 7d RE = 194 (Jul 23 weights 45 + Jul 24 run 149); chronic 28d avg ≈ 187/wk. Load is balanced; no spike risk.
- **⚠ Fri Jul 24 run avg HR 182** — plan called for "easy run 5 km, HR ≤155". HR 182 is Z4 tempo territory. Pattern continues: easy-run HR ceiling being breached repeatedly (Jul 16 HR 161, Jul 17 HR 169, Jul 24 HR 182). This is a PF-return risk and sub-60 build inefficiency — aerobic base is not being built at these HRs.
- **Mon Jul 27 easy run 6 km MISSED** — W19 started with a skipped session, continuing the W18 run-debt pattern. Two W18 planned runs (Wed Jul 22, Sun Jul 26) were also missed. Last confirmed run: Jul 24 (4 days ago).
- **🚨 Amashova: 9 days post-race, still no Strava upload.** Manual upload action needed.
- **Hollywoodbets (33d): at-risk.** Sub-60 interval sessions start W20 (Aug 5 — 5×800m @ 5:30/km). Run base remains thin with repeated missed and high-HR sessions.
- **Foot: 0/10.** No new entries. Daily prehab continues.


---

## Cycle auto — 2026-07-29

- **Sync at:** 2026-07-29T00:15:39Z
- **Data source:** cached (Strava unreachable)
- **Activity baseline:** 2 activities in last 7 days, 39 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-07-30

- **Sync at:** 2026-07-30T00:14:00Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 38 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 37 — 2026-07-30 (W19 run debt deepening · Sat long run critical · 31d Hollywoodbets)

- **Plan gate:** Current. W19 (27 Jul–2 Aug) covers today; plan `updated: 2026-07-23`; no triggers fired.
- **ACWR 1.04** — optimal (acute 7d RE=194; chronic 28d avg=187/wk). Load balanced but critically low for Hollywoodbets sub-60 build.
- **🚨 W19 — 5 consecutive missed sessions (Jul 25–29).** Last run: Jul 24 (6 days ago, avg HR **182** vs ≤155 ceiling — 9th consecutive easy-run HR breach). W19 plan through today: Mon easy run ❌ · Tue weights ❌ · Wed strides+form ❌ · Thu weights (today) = TBD. Zero running in W19 so far.
- **Sat Aug 1 = 10 km long run (first long run of Phase 5 / first 10 km since pre-PF).** Two days away. Non-negotiable — the sub-60 build cannot slip further. HR ≤155. If the foot holds at 10 km, the block stays on track.
- **Hollywoodbets 31 days (Aug 30).** W20 5×800m @ 5:30/km starts Aug 5 with essentially zero run base under it. Sub-60 attempt requires immediate and consistent run volume this week and next.
- **Amashova: 11 days post-race, still no Strava upload.** Outcome (finish/DNF) unknown. Manual upload action needed.
- **Foot: 0/10, resolved.** Daily prehab continues.


---

## Cycle auto — 2026-07-31

- **Sync at:** 2026-07-31T00:14:01Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 37 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-08-01

- **Sync at:** 2026-08-01T00:14:28Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 36 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 38 — 2026-08-01 (automated daily · ACWR 0.00 — worst of block · W19 zero runs · sub-60 alarm)

- **Plan gate:** Current. W19 (27 Jul–2 Aug) covers today (Sat); plan `updated: 2026-07-23`; injury log (Jul 6) older than plan; Hollywoodbets only active race (Aug 30, 29d). No triggers fired.
- **⚠ ACWR 0.00 — absolute block trough.** Acute 7-day RE = 0 (zero activities Jul 25–Aug 1); chronic 28-day avg = 187 RE/wk. Not injury risk — detraining risk. This is the lowest ACWR of the entire block, worse than the post-Imfolozi trough of 0.18 (Cycle 24) or the Jul 5 trough of 0.18.
- **🚨 W19 — zero Strava uploads Mon Jul 27 – Fri Jul 31 (5 sessions missed).** Planned: Mon easy run 6 km · Tue weights · Wed strides+form · Thu weights · Fri easy run 6 km. None logged. Today (Sat Aug 1) = **Long run 10 km** (first 10 km since pre-PF, non-negotiable). This is either a Strava upload gap or a genuine rest week — upload any completed activities from Garmin app.
- **🚨 Hollywoodbets 10K: 29 days.** W20 5×800m @ 5:30/km (Aug 5) is **4 days away** — the first critical sub-60 quality session. Entering it with ACWR=0 and zero W19 runs is a serious risk to session quality. If today's 10 km long run lands, ACWR will recover slightly but will still be below 0.5 entering W20. Plan on-target by prescription; execution is the gap.
- **🚨 Amashova: 13 days post-race, still no Strava upload (36 activities).** Outcome (finish/DNF) unknown. Manual Garmin/Wahoo upload action needed. If completed (RE ~600-800), ACWR would spike to 3.0+ — delay W19/W20 runs until it drops below 1.3.
- **Easy-run HR breach streak: 9 consecutive** (Jul 24 avg HR 182, most recent; all ≥161 avg vs ≤155 ceiling). No foot pain reported. Enforce ≤155 strictly on today's long run — it's the first 10 km since PF injury.
- **4-week adherence ~23%** (5 sessions logged out of ~22 planned, Jul 4 – Aug 1). Critical run sessions to hold from here: Wed Aug 5 (5×800m), Sat Aug 8 (11 km), Wed Aug 12 (4×1km), Sat Aug 15 (12 km), Wed Aug 19 (6×400m), Sat Aug 22 (5 km TT).
- **Foot: 0/10, resolved.** Daily prehab continues.


---

## Cycle auto — 2026-08-02

- **Sync at:** 2026-08-02T00:12:44Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 36 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 39 — 2026-08-02 (W19 closes at zero · W20 transition risk · 28d Hollywoodbets)

- **Plan gate:** Current. W19 (27 Jul–2 Aug) ends today; W20 (3–9 Aug) starts tomorrow. Plan `updated: 2026-07-23`. No staleness triggers fired.
- **W19 CONFIRMED ZERO.** Aug 1 long run (planned: 10 km, first post-PF, non-negotiable) did not appear in Strava sync at 2026-08-02T00:12:44Z (36 activities unchanged). W19 ends 0/6 active sessions — the worst week of the entire block and the second consecutive zero-activity stretch.
- **⚠ W20 transition risk.** 5×800m intervals (Wed Aug 5) arrive in 3 days with ACWR=0.00 and zero W19 run volume. **Mon Aug 3 easy 6 km (HR ≤155) is the critical first step** — do not skip it and do not let the HR creep above 155. The long run on Sat Aug 8 (11 km) must be the anchor recovery for the ACWR to climb toward 0.8 before Wed 12 Aug intervals.
- **Hollywoodbets 10K: 28 days.** 4-week adherence ~36% (8/22 sessions). Sub-60 requires a clean W20–W22 — every interval session and long run from here is non-negotiable.
- **Amashova: 14 days post-race, zero Strava upload.** Upload ASAP — if completed (RE ~600-800), it would retroactively change the chronic load picture and may justify W19's reduced output.
- **Foot: 0/10.** No change. Prehab continues.


---

## Cycle auto — 2026-08-03

- **Sync at:** 2026-08-03T00:18:43Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 36 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-08-04

- **Sync at:** 2026-08-04T00:16:26Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 35 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 40 — 2026-08-04 (W20 Mon also missed · 5×800m tomorrow · 26d Hollywoodbets)

- **Plan gate:** Current. W20 (3–9 Aug) covers today; plan `updated: 2026-07-23`. Hollywoodbets is 26 days out — not yet in the 7-day taper-needed window. No staleness triggers.
- **ACWR 0.00** — second consecutive week of flat-zero acute load. Chronic 28d avg = 187 RE/wk. This is not an injury spike; it is a detraining trough heading into the block's most critical quality weeks.
- **W20 Mon Aug 3 (easy 6 km) not on Strava** — first session of W20 missed, continuing the 11-day no-run streak (last run Jul 24, avg HR 182). Strava activity count dropped 36→35 vs yesterday (one activity deleted or privacy-changed; not a new run).
- **🚨 Wed Aug 5 = 5×800m @ 5:30/km — one day away.** This is the first and most important sub-60 quality session. Entering it with ACWR=0.00 and 11 days since last run. Warm up thoroughly (15 min easy); scale to 3×800m if legs feel flat rather than skipping it entirely.
- **Hollywoodbets 10K: 26 days.** Remaining non-negotiable sessions: Wed Aug 5 (5×800m), Sat Aug 8 (11 km), Wed Aug 12 (4×1km), Sat Aug 15 (12 km), Wed Aug 19 (6×400m), Sat Aug 22 (5 km TT). Missing even one more interval session puts sub-60 in serious jeopardy.
- **Amashova: 16 days post-race, still no Strava upload.** Upload from Garmin app ASAP.
- **Foot: 0/10.** No change. Prehab continues.


---

## Cycle auto — 2026-08-05

- **Sync at:** 2026-08-05T00:18:42Z
- **Data source:** Strava API
- **Activity baseline:** 0 activities in last 7 days, 35 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-08-06

- **Sync at:** 2026-08-06T00:20:14Z
- **Data source:** Strava API
- **Activity baseline:** 1 activities in last 7 days, 36 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.

---

## Cycle 41 — 2026-08-06 (W20 D4 · 5×800m confirmed not executed · 24d Hollywoodbets)

- **W20 Wed Aug 5 key session substituted:** Plan = 5×800m @ 5:30/km (first critical sub-60 session). Actual = 5.09 km run / 32:01 / avg HR 172 / RE 135. Neither intervals (HR should reach 185+) nor easy (ceiling ≤155). 10th consecutive easy-run HR breach.
- **ACWR 0.61** (acute 7d RE=135, chronic 28d avg=221/wk). Still below the 0.8 safe-band floor — undertraining entering the final 24-day build. Not an injury spike; a detraining risk.
- **Run vol 23.4 km / 28d** (target 30 km). Fastest pace 6:05/km (Jul 24) vs sub-60 target 5:59/km. No interval sessions completed in the block.
- **Hollywoodbets 10K: 24 days.** Remaining non-negotiables: Sat Aug 8 (11 km long run), Wed Aug 12 (4×1km @ 5:55/km), Sat Aug 15 (12 km), Wed Aug 19 (6×400m), Sat Aug 22 (5 km TT). Sub-60 attempt is seriously at risk — at minimum Wed Aug 12 intervals must land. Foot: 0/10, resolved. Plan current.


---

## Cycle auto — 2026-08-07

- **Sync at:** 2026-08-07T00:22:36Z
- **Data source:** Strava API
- **Activity baseline:** 2 activities in last 7 days, 37 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.


---

## Cycle auto — 2026-08-08

- **Sync at:** 2026-08-08T00:20:24Z
- **Data source:** cached (Strava unreachable)
- **Activity baseline:** 2 activities in last 7 days, 37 in 90-day window.
- **Notes:** Auto-cycle (resilient build · on-demand data worker). Manual /my-training review cycles are logged separately.
