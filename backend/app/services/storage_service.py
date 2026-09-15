import os
import shutil
from pathlib import Path
import uuid
from backend.app.config import settings

class StorageService:
    def __init__(self, upload_dir: Path = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_bytes: bytes, filename: str) -> tuple[str, str]:
        """
        Saves file locally and returns (file_id, file_path).
        """
        ext = Path(filename).suffix
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{ext}"
        destination = self.upload_dir / safe_filename
        
        with open(destination, "wb") as f:
            f.write(file_bytes)
            
        return file_id, str(destination)

    def get_file_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path

storage_service = StorageService()
