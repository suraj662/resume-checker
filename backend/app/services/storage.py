from supabase import create_client
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = "resumes"
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            if self.bucket_name not in bucket_names:
                self.client.storage.create_bucket(
                    self.bucket_name,
                    {"public": True}
                )
                logger.info(f"✅ Created bucket: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"⚠️ Bucket check warning: {e}")

    async def upload_resume(self, file_content: bytes, filename: str, user_id: str) -> str:
        # Generate a unique file path
        file_ext = filename.split('.')[-1]
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"

        # Upload to Supabase
        self.client.storage.from_(self.bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": f"application/{file_ext}"}
        )

        # Return public URL
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)

# Create the singleton instance
storage_service = SupabaseStorageService()