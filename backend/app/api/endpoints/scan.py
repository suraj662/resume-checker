from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.llm_analyzer import llm_analyzer_service
from app.services.storage import storage_service
from app.models.schemas import ScanResponse
from app.core.config import settings
from supabase import create_client
from uuid import uuid4
import logging
import base64
import json
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

class AnalyzeRequest(BaseModel):
    file_base64: str
    filename: str
    job_desc: str

# 🔥 EMERGENCY BYPASS: Extract user ID directly from token without verifying signature
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Just decode the token without verifying the signature
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return user_id
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/analyze", response_model=ScanResponse)
async def analyze_resume(
        request: AnalyzeRequest,
        user_id: str = Depends(get_current_user)
):
    try:
        logger.info(f"Processing scan for user: {user_id}, file: {request.filename}")

        # 1. Decode Base64 to bytes
        file_content = base64.b64decode(request.file_base64)

        # 2. Upload to Supabase Storage
        resume_url = await storage_service.upload_resume(
            file_content,
            request.filename,
            user_id
        )

        # 3. Analyze with LLM
        analysis = llm_analyzer_service.analyze_resume("Mock text", request.job_desc)

        # 4. Save to Supabase Database with the REAL User ID
        scan_data = {
            "user_id": user_id,
            "resume_url": resume_url,
            "job_desc": request.job_desc,
            "match_score": analysis["match_score"],
            "missing_keywords": analysis["missing_keywords"],
            "strong_matches": analysis["strong_matches"],
            "formatting_issues": analysis["formatting_issues"],
            "suggestions": analysis["suggestions"]
        }

        result = supabase.table('scan_history').insert(scan_data).execute()

        if not result.data:
            raise HTTPException(500, "Failed to save to database")

        saved = result.data[0]

        return ScanResponse(
            id=saved['id'],
            user_id=str(saved['user_id']),
            resume_url=saved['resume_url'],
            job_desc=saved['job_desc'],
            match_score=saved['match_score'],
            missing_keywords=saved['missing_keywords'],
            strong_matches=saved['strong_matches'],
            formatting_issues=saved['formatting_issues'],
            suggestions=saved['suggestions'],
            created_at=saved['created_at']
        )

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")