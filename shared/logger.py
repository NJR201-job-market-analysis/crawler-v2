import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

# 配置 logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f'logs/crawler_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(),
    ],
)


# 全域 logger
logger = logging.getLogger(__name__)
