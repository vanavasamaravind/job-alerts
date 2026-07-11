# Search queries are consolidated (multiple titles OR'd per query) to stay
# within JSearch's free-tier quota: 2 queries x 2 runs/day x 31 days = 124 requests/month (cap is 200).
SEARCH_QUERIES = [
    "Network Automation Engineer OR NetDevOps Engineer OR Network Engineer jobs in United States",
    "DevOps Engineer OR Site Reliability Engineer jobs in United States",
]

COUNTRY = "us"
DATE_POSTED = "today"

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
