from shared.logger import logger
from .tasks import crawl_1111_jobs
from .constants import JOB_CATEGORIES

# 定義要爬取的分ㄊ
categories = [
    # 雲服務/雲計算
    "140600",
    # 網站技術主管
    "140211",
    # 網站程式設計師
    "140213",
    "140802",
    "140803",
    "140804",
    "140805",
    "140806",
    "140810",
    "140301",
    # 可以繼續添加更多分類
]

logger.info("🚀 開始發送 %s 個 1111 爬蟲任務", len(categories))

tasks = []

# 為每個分類創建一個任務
for category_id in categories:

    category_name = JOB_CATEGORIES[category_id]

    task = crawl_1111_jobs.s(category_id=category_id)
    task.apply_async(queue="crawler-queue")

    tasks.append(task)
    logger.info(
        "📤 已發送 1111 爬蟲任務: %s | %s | ID: %s", category_id, category_name, task.id
    )

logger.info("✅ 所有 1111 爬蟲任務已發送完成，共 %s 個任務", len(tasks))
