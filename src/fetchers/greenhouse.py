# import requests
# from bs4 import BeautifulSoup
# from typing import List
# from ..models import JobPosting

# def _textify(soup: BeautifulSoup) -> str:
#     # crude but effective for MVP
#     return "\n".join([t.get_text(" ", strip=True) for t in soup.find_all(["h1","h2","h3","p","li"])])

# def fetch_greenhouse(board_url: str) -> List[JobPosting]:
#     # board_url like: https://boards.greenhouse.io/<company>
#     r = requests.get(board_url, timeout=20, headers={"User-Agent": "job-match-agent/0.1"})
#     r.raise_for_status()
#     soup = BeautifulSoup(r.text, "lxml")

#     company = board_url.rstrip("/").split("/")[-1]
#     links = []
#     for a in soup.select("a"):
#         href = a.get("href")
#         if not href:
#             continue
#         # greenhouse job links often contain "/jobs/" or similar
#         if "/jobs/" in href:
#             if href.startswith("/"):
#                 href = "https://boards.greenhouse.io" + href
#             links.append(href)

#     # de-dupe
#     links = list(dict.fromkeys(links))

#     out: List[JobPosting] = []
#     for url in links[:250]:  # safety cap
#         jr = requests.get(url, timeout=20, headers={"User-Agent": "job-match-agent/0.1"})
#         if jr.status_code != 200:
#             continue
#         jsoup = BeautifulSoup(jr.text, "lxml")

#         title = (jsoup.find("h1").get_text(strip=True) if jsoup.find("h1") else "Untitled")
#         location_el = jsoup.select_one(".location")  # common class
#         location = location_el.get_text(strip=True) if location_el else None

#         desc = _textify(jsoup)
#         job_id = url.split("/")[-1]

#         out.append(JobPosting(
#             id=str(job_id),
#             title=title,
#             company=company,
#             location=location,
#             remote=None,
#             url=url,
#             posted_date=None,
#             description=desc,
#             source="greenhouse",
#         ))
#     return out