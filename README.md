i am aravuind# Daily Job Alert Bot

Fetches job postings via the JSearch API (RapidAPI) and emails the ones posted
since the last run. Runs twice a day (morning + evening) via a scheduled
Claude Code cloud routine, so postings surface within hours instead of once a day.

## How it works

- `config.py` defines the search queries (job titles OR'd together, to stay
  within JSearch's free-tier request quota) and each run's look-back window.
- `job_alert.py` calls JSearch, filters results to jobs posted within that
  run's window, and emails any it finds via Gmail SMTP. No pip installs
  needed — stdlib only.
- Stateless: instead of persisting a "already seen" list between runs, each
  run just asks for jobs posted in the last N hours (sized to the gap since
  the previous run). Simpler, and avoids needing to commit state back to git
  from an ephemeral cloud sandbox.

## Setup

1. Copy `.env.example` to `.env` and fill in:
   - `RAPIDAPI_KEY` — from your RapidAPI account, subscribed to the JSearch API (Basic/free tier).
   - `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` — a Gmail account with an App Password (Google Account > Security > 2-Step Verification > App Passwords).
   - `RECIPIENT_EMAIL` — where the digest gets sent.
2. Run manually: `python job_alert.py manual --dry-run` (prints, doesn't send) or `python job_alert.py manual` (sends).

## Scheduled runs

Runs as a Claude Code cloud routine, twice daily (8:00 AM and 6:00 PM Pacific Time).
Run labels (`morning` / `evening`) select the look-back window from `config.WINDOW_HOURS`.
Manage routines at https://claude.ai/code/routines.
