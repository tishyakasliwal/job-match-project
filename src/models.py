from pydantic import BaseModel
from typing import Optional

class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    description: str #job overview
    url: str
    remote: Optional[bool] = None
    posted_date: Optional[str] = None
    details: Optional[str] = None  #field for extra details - responsibilities, qualifications, etc.
    source: str  # "lever" | "greenhouse" | "fallback"