# Setup — One-time Strava API + GitHub secrets

The daily 04:07 SAST cron is a GitHub Actions workflow that needs **three repo secrets** before it can run. Set these once and you're done.

## Step 1 — Create a Strava API app

1. Open <https://www.strava.com/settings/api> while logged into Strava.
2. Click **Create & Manage Your App**.
3. Fill in:
   - **Application Name:** `my-training-personal`
   - **Category:** any (Health & Fitness is fine)
   - **Club:** leave blank
   - **Website:** `http://localhost`
   - **Application Description:** Personal training dashboard
   - **Authorization Callback Domain:** `localhost`
4. Click **Create**.
5. Note down the **Client ID** and **Client Secret** shown on the next page.

## Step 2 — One-time OAuth to get a refresh token

The dashboard cron uses a long-lived refresh token. To get one:

1. Open this URL in your browser (replace `<CLIENT_ID>` with yours):

   ```
   https://www.strava.com/oauth/authorize?client_id=<CLIENT_ID>&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all
   ```

2. Click **Authorize**. Strava will redirect you to a URL like:

   ```
   http://localhost/?state=&code=<LONG_CODE_HERE>&scope=read,activity:read_all
   ```

   The page will fail to load (there's no server at localhost) but that's expected — **copy the `code=` value from the address bar**.

3. Exchange the code for a refresh token. In a terminal:

   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -d client_id=<CLIENT_ID> \
     -d client_secret=<CLIENT_SECRET> \
     -d code=<CODE_FROM_STEP_2> \
     -d grant_type=authorization_code
   ```

4. The response will be JSON. Note the `refresh_token` value (long string starting with letters).

## Step 3 — Set the three GitHub secrets

```bash
gh secret set STRAVA_CLIENT_ID --repo naickert/theo-training-log --body "<CLIENT_ID>"
gh secret set STRAVA_CLIENT_SECRET --repo naickert/theo-training-log --body "<CLIENT_SECRET>"
gh secret set STRAVA_REFRESH_TOKEN --repo naickert/theo-training-log --body "<REFRESH_TOKEN>"
```

Or via the GitHub web UI: <https://github.com/naickert/theo-training-log/settings/secrets/actions> → **New repository secret** for each of the three.

## Step 4 — Test the workflow manually

Once secrets are set, trigger a manual run to validate:

```bash
gh workflow run "Daily training dashboard" --repo naickert/theo-training-log
```

Then watch:

```bash
gh run watch --repo naickert/theo-training-log
```

If it succeeds, a fresh `index.html` and `training-dashboard-YYYY-MM-DD.html` will be committed and pushed within 2–3 minutes.

## Step 5 — Done

After successful manual test, the cron will fire automatically at 04:07 SAST (02:07 UTC) every day. No further action needed.

## Troubleshooting

- **`401 Unauthorized` from Strava** — refresh token expired (rare; usually only after a Strava password reset). Redo Step 2 and update the `STRAVA_REFRESH_TOKEN` secret.
- **`Rate limit exceeded`** — Strava allows 200 calls per 15 min. Daily use is far under this.
- **Workflow doesn't run** — check Actions are enabled at <https://github.com/naickert/theo-training-log/settings/actions>.

## Adding a new race

Edit `knowledge/race-calendar.md` directly in GitHub or locally + push. The next cron run picks it up.

## Manual run from your Mac

The local skill `~/.claude/skills/my-training/` can also do this — useful for ad-hoc updates or if the cron is broken. Tell Claude `/my-training` and it will run the same workflow locally (using Chrome scraping instead of API).
