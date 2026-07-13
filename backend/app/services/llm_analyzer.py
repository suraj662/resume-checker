import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMAnalyzerService:
    def __init__(self):
        logger.info("✅ Ultra-Stable Mock AI Mode Activated")

    def analyze_resume(self, resume_text: str, job_desc: str) -> dict:
        # Extract keywords dynamically from job description
        job_lower = job_desc.lower()

        missing = []
        strong = []
        score = 75

        if "java" in job_lower:
            strong.append("Java")
            score += 5
        else:
            missing.append("Java")

        if "spring" in job_lower or "boot" in job_lower:
            strong.append("Spring Boot")
            score += 5
        else:
            missing.append("Spring Boot")

        if "sql" in job_lower or "database" in job_lower:
            strong.append("SQL")
            score += 4
        else:
            missing.append("SQL")

        if "api" in job_lower or "rest" in job_lower:
            strong.append("REST API")
            score += 5
        else:
            missing.append("REST API")

        if "aws" in job_lower or "cloud" in job_lower:
            strong.append("AWS")
            score += 4
        else:
            missing.append("AWS")

        if "hibernate" in job_lower or "jpa" in job_lower:
            strong.append("Hibernate/JPA")
            score += 3
        else:
            missing.append("Hibernate/JPA")

        score = min(score, 100)  # Cap at 100

        return {
            "match_score": score,
            "missing_keywords": missing,
            "strong_matches": strong,
            "formatting_issues": [
                "Use bullet points for your technical skills",
                "Add specific metrics (e.g., improved performance by 20%)",
                "Include a professional summary at the top"
            ],
            "suggestions": "Highlight your experience with Java frameworks. Add more specific technologies and tools you've worked with."
        }

llm_analyzer_service = LLMAnalyzerService()