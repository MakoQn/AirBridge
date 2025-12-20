import subprocess
import datetime
import os
from src.utils.config import Config
from src.services.minio_service import MinioService

def create_backup():
    conf = Config()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join("db_backups", filename)
    
    if not os.path.exists("db_backups"):
        os.makedirs("db_backups")
    
    env = os.environ.copy()
    env["PGPASSWORD"] = conf.DB_PASSWORD
    
    command = [
        "pg_dump",
        "-h", conf.DB_HOST,
        "-p", conf.DB_PORT,
        "-U", conf.DB_USER,
        "-F", "c",
        "-f", filepath,
        conf.DB_NAME
    ]
    
    try:
        subprocess.run(command, env=env, check=True)
        
        minio = MinioService()
        minio.upload_file(filepath, f"backups/{filename}")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
    except Exception as e:
        print(e)
        raise e

if __name__ == "__main__":
    create_backup()