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
