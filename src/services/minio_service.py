from minio import Minio
from src.utils.config import Config

class MinioService:
    def __init__(self):
        self.config = Config()
        self.client = Minio(
            endpoint=self.config.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
            secure=self.config.MINIO_SECURE
        )
        self.bucket = self.config.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, file_path, object_name):
        try:
            self.client.fput_object(self.bucket, object_name, file_path)
            return f"http://{self.config.MINIO_ENDPOINT}/{self.bucket}/{object_name}"
        except Exception:
            return None