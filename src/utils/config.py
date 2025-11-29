import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    
    MINIO_ENDPOINT = os.environ["MINIO_ENDPOINT"]
    MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
    MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]
    MINIO_BUCKET_NAME = os.environ["MINIO_BUCKET_NAME"]
    MINIO_SECURE = os.environ["MINIO_SECURE"].lower() == "true"
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def minio_config(self):
        return {
            "endpoint": self.MINIO_ENDPOINT,
            "access_key": self.MINIO_ACCESS_KEY,
            "secret_key": self.MINIO_SECRET_KEY,
            "secure": self.MINIO_SECURE
        }