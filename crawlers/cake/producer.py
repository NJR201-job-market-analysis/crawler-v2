from .tasks import crawl_cake_jobs
from shared.logger import logger

# 定義要爬取的分類和職位類型
categories = [
    ("software-developer", None),
    ("start-up", None),
    ("overseas-company", "it"),
    ("million-salary", "it"),
    ("top500-companies", "it"),
    ("digital-nomad", "it"),
    ("remote-work", "it"),
    ("bank", "it"),
    # 可以繼續添加更多分類
]

logger.info("🚀 開始發送 %s 個爬蟲任務", len(categories))

tasks = []

# 為每個分類創建一個任務
for category, job_type in categories:

    task = crawl_cake_jobs.s(category=category, job_type=job_type)
    task.apply_async(queue="crawler-queue")

    tasks.append(task)
    logger.info("📤 已發送任務: %s | %s | ID: %s", category, job_type, task.id)

logger.info("✅ 所有任務已發送完成，共 %s 個任務", len(tasks))
