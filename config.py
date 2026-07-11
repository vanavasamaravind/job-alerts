# Search queries are consolidated (multiple titles OR'd per query) to stay
# within JSearch's free-tier quota: 2 queries x 2 runs/day x 31 days = 124 requests/month (cap is 200).
#
# Note: JSearch's matching degrades badly past ~3 OR'd titles in one query
# (tested: 5-7 title OR chains returned 0 results even over a 3-day window).
# Bare "Automation Engineer" / "Test Engineer" alone also pull in a lot of
# non-networking noise (aerospace/PCBA/QA hardware roles), so query 2 uses a
# natural-language phrase instead of OR chaining to keep it networking-scoped.
SEARCH_QUERIES = [
    "Network Automation Engineer OR NetDevOps Engineer OR Network Engineer jobs in United States",
    "Networking test automation engineer jobs in United States",
]

COUNTRY = "us"
DATE_POSTED = "today"

# JSearch's best-effort experience-level filter. Cuts out clearly-junior
# postings, but coverage depends on whether a listing has parseable experience
# text -- some 3+ yr roles may still be excluded, and it can shrink an
# already-small daily pool to zero on quiet days.
JOB_REQUIREMENTS = "more_than_3_years_experience"

# Each run is stateless: it only shows jobs posted within WINDOW_HOURS[run_label]
# hours, sized to the actual gap since the previous run. A small overlap is
# intentional (better a rare duplicate than a missed posting at the boundary).
# Morning (8:00 AM PT) follows the previous evening run (6:00 PM PT, ~14h gap).
# Evening (6:00 PM PT) follows the same day's morning run (~10h gap).
WINDOW_HOURS = {
    "morning": 15,
    "evening": 11,
    "manual": 24,
}
