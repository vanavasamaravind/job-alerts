"""Fetch recent job postings via JSearch and email the ones posted since the last run.

Stateless by design: each run only reports jobs posted within a run-specific
time window (see config.WINDOW_HOURS), so it works the same locally or as a
one-shot cloud routine run with no persisted state or git commit-back needed.
Stdlib only, no pip installs required.
"""
import json
import os
import smtplib
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path

from config import SEARCH_QUERIES, COUNTRY, DATE_POSTED, WINDOW_HOURS, JOB_REQUIREMENTS

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search-v2"


def load_env():
    env = dict(os.environ)
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env.setdefault(key.strip(), value.strip())
    return env


def fetch_jobs(query, api_key):
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": DATE_POSTED,
        "country": COUNTRY,
        "job_requirements": JOB_REQUIREMENTS,
    }
    url = f"{JSEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") != "OK":
        raise RuntimeError(f"JSearch error for query {query!r}: {data}")
    return data.get("data", {}).get("jobs", [])


def format_email(jobs, run_label, window_hours):
    lines = [
        f"Job postings from the last {window_hours}h ({run_label} run, {len(jobs)} found):",
        "",
    ]
    for job in sorted(jobs, key=lambda j: j.get("job_posted_at_timestamp", 0), reverse=True):
        title = job.get("job_title", "Unknown title")
        company = job.get("employer_name", "Unknown company")
        city = job.get("job_city") or ""
        state_ = job.get("job_state") or ""
        location = ", ".join(p for p in [city, state_] if p) or "Location not listed"
        remote = " (Remote)" if job.get("job_is_remote") else ""
        posted = job.get("job_posted_at", "")
        link = job.get("job_apply_link") or job.get("job_google_link") or ""
        lines.append(f"- {title} | {company} | {location}{remote} | posted {posted}")
        lines.append(f"  {link}")
        lines.append("")
    return "\n".join(lines)


def send_email(env, subject, body):
    sender = env.get("GMAIL_ADDRESS")
    password = env.get("GMAIL_APP_PASSWORD")
    recipient = env.get("RECIPIENT_EMAIL", sender)
    if not sender or not password:
        raise RuntimeError("GMAIL_ADDRESS / GMAIL_APP_PASSWORD not set in .env")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender, password.replace(" ", ""))
        server.sendmail(sender, [recipient], msg.as_string())


def main():
    run_label = sys.argv[1] if len(sys.argv) > 1 else "manual"
    dry_run = "--dry-run" in sys.argv
    window_hours = WINDOW_HOURS.get(run_label, WINDOW_HOURS["manual"])

    env = load_env()
    api_key = env.get("RAPIDAPI_KEY")
    if not api_key:
        raise RuntimeError("RAPIDAPI_KEY not set in .env")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    all_jobs = {}
    for query in SEARCH_QUERIES:
        try:
            jobs = fetch_jobs(query, api_key)
        except Exception as exc:
            print(f"Query failed: {query!r}: {exc}", file=sys.stderr)
            continue
        for job in jobs:
            job_id = job.get("job_id")
            posted_ts = job.get("job_posted_at_timestamp")
            if not job_id or posted_ts is None:
                continue
            posted_at = datetime.fromtimestamp(posted_ts, tz=timezone.utc)
            if posted_at >= cutoff:
                all_jobs[job_id] = job

    recent_jobs = list(all_jobs.values())

    if not recent_jobs:
        print(f"No jobs posted in the last {window_hours}h; no email sent.")
        return

    body = format_email(recent_jobs, run_label, window_hours)
    subject = f"Job Alert ({run_label}): {len(recent_jobs)} posting(s)"
    print(body)
    if dry_run:
        print("[dry-run] Email not sent.")
        return

    send_email(env, subject, body)
    print(f"Sent email with {len(recent_jobs)} jobs.")


if __name__ == "__main__":
    main()
