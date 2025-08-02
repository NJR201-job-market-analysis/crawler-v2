from shared.logger import logger
from .tasks import crawl_104_jobs
from .category_dict import CATEGORIES_DICT

# 定義要爬取的分類和職位類型
categories = [
    # 軟體工程類人員
    "2007001000",
    # 前端工程師
    "2007001015",
    # 可以繼續添加更多分類
]

logger.info("🚀 開始發送 %s 個 104 爬蟲任務", len(categories))

tasks = []

# 為每個分類創建一個任務
for category, job_type in categories:
    category_name = CATEGORIES_DICT[category]

    task = crawl_104_jobs.s(category_id=category)
    task.apply_async(queue="crawler-queue")

    tasks.append(task)
    logger.info("📤 已發送 104 爬蟲任務: %s | ID: %s", category_name, task.id)

logger.info("✅ 所有 104 爬蟲任務已發送完成，共 %s 個任務", len(tasks))
