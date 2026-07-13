import io
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class FileParserService:
    async def parse_file(self, file: UploadFile) -> str:
        # Read file content
        content = await file.read()

        # Just return a dummy text for now so we can test the API!
        return f"Extracted text from {file.filename} (Test successful!)"

file_parser_service = FileParserService()