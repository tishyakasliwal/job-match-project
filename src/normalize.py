from typing import List
from .models import JobPosting
from .fetchers.lever import fetch_lever
#from .fetchers.greenhouse import fetch_greenhouse
#from .fetchers.html_fallback import fetch_fallback

def fetch_jobs_from_url(url: str) -> List[JobPosting]:
    u = url.lower()
    if "lever.co" in u:  # Matches both jobs.lever.co and api.lever.co
        return fetch_lever(url)
    # if "boards.greenhouse.io" in u:
    #     return fetch_greenhouse(url)
    return []

def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
    seen = set()
    out = []
    for j in jobs:
        key = (j.company.lower(), j.title.lower(), (j.location or "").lower(), j.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out