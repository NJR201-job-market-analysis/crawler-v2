import os
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env 文件
env_file = Path(__file__).parent / '../.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ 載入 .env 文件: {env_file}")
else:
    print(f"⚠️ .env 文件不存在: {env_file}")

WORKER_ACCOUNT = os.environ.get("WORKER_ACCOUNT", "worker")
WORKER_PASSWORD = os.environ.get("WORKER_PASSWORD", "worker")

# 在 Docker 環境中使用容器名稱，在本地開發時使用 localhost
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))

MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_ACCOUNT = os.environ.get("MYSQL_ACCOUNT", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "test")
