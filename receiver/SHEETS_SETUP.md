# Google Sheets check-in — setup (one-time)

Union Pantry mode writes to a Google Sheet. There are two ways to connect. **Keystroke and
Textbook Library modes need none of this** — they don't touch Google.

- **Service account (recommended for sharing the app)** — no one ever signs in. You bundle one
  key; each roster sheet is just *shared* with the service account's email. No sign-in, no
  7-day token expiry, no "unverified app" warning, no verification — ever. Best when handing
  the app to others.
- **OAuth "Sign in with Google"** — each operator signs in with their own Google account. Fine
  for personal use, but in a personal (non-Workspace) project it's stuck in **Testing** mode:
  logins re-prompt every 7 days and show an "unverified app" screen. See §OAuth below.

The app auto-detects which to use: if a bundled `service_account.json` is present it uses the
service account; otherwise it falls back to OAuth.

## Service account (recommended, ~5 min once)

1. <https://console.cloud.google.com/> → your project → **APIs & Services → Library →**
   **Google Sheets API → Enable** (if it isn't already).
2. **IAM & Admin → Service Accounts → Create service account.** Name it (e.g.
   `anusa-scanner-sheets`). **Skip** the optional roles/access steps → **Done**.
3. Open the new service account → **Keys → Add key → Create new key → JSON → Create.** A JSON
   file downloads.
4. Rename it to **`service_account.json`** and put it in `receiver/` (next to `build_mac.sh`).
   It's git-ignored — never commit it.
5. Copy the service account's **email** — it looks like
   `anusa-scanner-sheets@your-project.iam.gserviceaccount.com`.
6. **For each roster sheet:** open it → **Share** → paste that email → set **Editor** → Send.
   (Uncheck "Notify people" — it's not a real inbox.)
7. Build: `bash build_mac.sh` (it bundles the key). Launch — under Union Pantry it shows
   **✓ Service account**; no sign-in button. Paste a shared sheet's URL and go.

**Security:** the key is bundled inside the distributed `.app` and can be extracted. Its reach
is limited to sheets you've shared with this service account — so use a **dedicated** service
account for this, share only event rosters with it, and if the key ever leaks, rotate it
(Service account → Keys → delete the old one, create a new one, rebuild). The built `.app` and
the key are git-ignored, so they're never committed.

---

## OAuth (alternative — per-user sign-in)

## 1. Create an OAuth client (~5 min, once)

1. Go to <https://console.cloud.google.com/> and **create a project** (e.g. `anusa-scanner`).
2. **APIs & Services → Library →** search **Google Sheets API → Enable**.
3. **APIs & Services → OAuth consent screen:**
   - User type: **External** → Create.
   - App name `ANUSA Scanner`, your email as support + developer contact. Save.
   - **Scopes:** add `.../auth/spreadsheets` (read/write Sheets). Save.
   - **Test users:** add every Google account that will run the scanner (yours to
     start). Save. *(Test mode is fine for a handful of people; tokens re-prompt
     every 7 days. To make logins persistent, later hit "Publish app" — it stays
     usable while "unverified", just shows a one-time "Google hasn't verified this
     app → Advanced → Go to app" screen.)*
4. **APIs & Services → Credentials → Create credentials → OAuth client ID:**
   - Application type: **Desktop app** → Create.
   - **Download JSON**, rename it to **`credentials.json`**, and put it next to
     `sheets_auth_spike.py` (in `receiver/`).

`credentials.json` and the generated `token.json` are git-ignored — never commit them.

## 2. Install deps

```
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

## 3. Run the spike

Auth + inspect a sheet (no writes) — a browser opens for sign-in the first time:

```
python3 sheets_auth_spike.py --url "https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0"
```

It prints the tabs, the header row, and row count. Use those headers to pick your
columns, then test an actual tick:

```
python3 sheets_auth_spike.py --url "…" \
    --id-col "Student ID" --tick-col today --name-col "Name" --student u8221537
```

- `--id-col` / `--tick-col` accept a **column letter** (`C`, `H`) or a **header name**.
- `--tick-col today` auto-detects a header matching today's date (handles the
  "different column each day" case).
- `--student` may include the `u` or not — both match.

Expected output ends in one of:

```
STATUS: checked-in  ·  Jane Doe  (ticked 'Sheet1'!H5)
STATUS: already     ·  Jane Doe  (row 5 already TRUE)
STATUS: not-registered  (u8221537 not found in column C)
```

Those three are exactly the statuses the Mac app will send back to the phone over
MQTT once this is wired in.

## What comes after the spike works

1. Move `get_service` + the normalize/resolve/tick helpers into the receiver.
2. Add a **Google Sheet** mode to the receiver UI: **Sign in with Google**, sheet
   URL field, and dropdowns for ID / tick / name columns (populated from the header
   row; tick defaults to today's-date column).
3. On each scan: look up → flip `FALSE`→`TRUE` → publish `{t:'checkin', status, name}`
   back to the phone, which shows `checked-in` / `already` / `not registered`.
4. If Sheets is unreachable: report `error` and stop (no queue), per spec.
