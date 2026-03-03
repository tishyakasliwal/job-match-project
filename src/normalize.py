from typing import List
from .models import JobPosting
from .fetchers.lever import fetch_lever
#from .fetchers.greenhouse import fetch_greenhouse
#from .fetchers.html_fallback import fetch_fallback

def fetch_jobs_from_url(url: str) -> List[JobPosting]:
    """
    Route URL to appropriate ATS fetcher based on domain.
    
    Args:
        url: Job board URL (e.g., https://api.lever.co/v0/postings/company)
        
    Returns:
        List of JobPosting objects from that board, or empty list if ATS not supported
        
    Currently Supported:
        - Lever
    """
    u = url.lower()
    if "lever.co" in u:  # Matches both jobs.lever.co and api.lever.co
        return fetch_lever(url)
    # if "boards.greenhouse.io" in u:
    #     return fetch_greenhouse(url)
    return []

def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
    """
    Remove duplicate job postings from list.
    
    Args:
        jobs: List of JobPosting objects (may contain duplicates)
        
    Returns:
        List with duplicates removed based on (company, title, location, url)
        
    Logic:
        - Creates a unique key for each job: (company, title, location, url)
        - Skips jobs with duplicate keys (keeps first occurrence)
        - Comparison is case-insensitive
    """
    seen = set()
    out = []
    for j in jobs:
        key = (j.company.lower(), j.title.lower(), (j.location or "").lower(), j.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out