from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ScanResponse(BaseModel):
    id: UUID
    user_id: UUID
    resume_url: str
    job_desc: str
    match_score: int
    missing_keywords: List[str]
    strong_matches: List[str]
    formatting_issues: List[str]
    suggestions: Optional[str]
    created_at: datetime
