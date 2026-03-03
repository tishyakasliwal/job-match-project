from bs4 import BeautifulSoup
import requests
from typing import List
from datetime import datetime
from ..models import JobPosting

def _html_to_text(html: str) -> str:
    """Convert Lever HTML list content to clean bullet text."""
    if not html:
        return ""
    soup = BeautifulSoup(f"<ul>{html}</ul>", "lxml")
    bullets = [li.get_text(" ", strip=True) for li in soup.find_all("li")]
    return "\n".join(f"- {b}" for b in bullets)

def _extract_details(item: dict) -> str:
    """
    Combine all 'lists' sections into a single details string.
    Example:
    CORE RESPONSIBILITIES:
    - ...
    WHAT WE REQUIRE:
    - ...
    """
    sections = []

    for section in item.get("lists", []):
        header = (section.get("text") or "").strip()
        content_html = section.get("content") or ""

        bullets_text = _html_to_text(content_html)

        if header or bullets_text:
            block = ""
            if header:
                block += header.upper() + ":\n"
            if bullets_text:
                block += bullets_text
            sections.append(block.strip())

    return "\n\n".join(sections)

def fetch_lever(board_url: str) -> List[JobPosting]:
    # board_url can be: https://jobs.lever.co/<company> or https://api.lever.co/v0/postings/<company>
    # Extract company name and use API endpoint
    company = board_url.rstrip("/").split("/")[-1]
    api_url = f"https://api.lever.co/v0/postings/{company}"
    r = requests.get(api_url, timeout=20, headers={"User-Agent": "job-match-agent/0.1"})
    r.raise_for_status()
    data = r.json()
    out: List[JobPosting] = []
    for item in data:
        # Lever fields may vary slightly; keep it robust.
        job_id = item.get("id") or item.get("hostedUrl") or item.get("applyUrl")
        title = item.get("text") or item.get("title") or "Untitled"
        categories = item.get("categories") or {}
        location = categories.get("location") or item.get("categories", {}).get("location")

        desc = item.get("descriptionPlain") or item.get("description") or ""
        if not desc:
            # sometimes description is HTML under "description"
            desc = item.get("description", "")

        # NEW: extract details from lists
        details = _extract_details(item)

        # NEW: convert createdAt -> readable date
        created_ms = item.get("createdAt")
        posted_date = None
        if created_ms:
            posted_date_obj = datetime.fromtimestamp(created_ms / 1000)
            posted_date = posted_date_obj.strftime("%Y-%m-%d")
            # Check if posted date is more than 10 old
            days_old = (datetime.now() - posted_date_obj).days
            if days_old > 10:
                continue # skip old postings


        url = item.get("hostedUrl") or item.get("applyUrl") or board_url
        out.append(JobPosting(
            id=str(job_id),
            title=title,
            company=company,
            location=location,
            remote=None,
            url=url,
            posted_date=posted_date,
            description=desc,
            details=details,
            source="lever",
        ))
    return out

# out = fetch_lever("https://api.lever.co/v0/postings/whoop")
# print(out)