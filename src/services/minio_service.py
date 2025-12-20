import json
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
        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.client.make_bucket(self.bucket)
        
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket}/*"]
                }
            ]
        }
        try:
            self.client.set_bucket_policy(self.bucket, json.dumps(policy))
        except Exception:
            pass

    def upload_file(self, file_path, object_name):
        try:
            self.client.fput_object(self.bucket, object_name, file_path)
            return f"http://{self.config.MINIO_ENDPOINT}/{self.bucket}/{object_name}"
        except Exception:
            return None