import logging
from datetime import datetime
from pathlib import Path

# 獲取項目根目錄並創建 logs 目錄
project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# 配置 logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            logs_dir / f'crawler_{datetime.now().strftime("%Y%m%d")}.log',
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)


# 全域 logger
logger = logging.getLogger(__name__)
