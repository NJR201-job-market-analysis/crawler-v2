from shared.logger import logger
from .tasks import crawl_1111_jobs
from .constants import job_categories

logger.info("🚀 開始發送 %s 個 1111 爬蟲任務", len(job_categories))

tasks = []

# 為每個分類創建一個任務
for category in job_categories:

    task = crawl_1111_jobs.s(category=category)
    task.apply_async(queue="crawler-queue")

    tasks.append(task)
    logger.info("📤 已發送 1111 爬蟲任務: %s | ID: %s", category["name"], task.id)

logger.info("✅ 所有 1111 爬蟲任務已發送完成，共 %s 個任務", len(tasks))
