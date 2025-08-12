from shared.logger import logger
from .tasks import crawl_yourator_jobs

job_categories = [
	"前端工程",
	"後端工程",
	"全端工程",
	"Android工程師",
	"iOS工程師",
	"遊戲開發",
	"測試工程",
	"資料庫",
	"DevOps / SRE",
	"區塊鏈工程師",
	"行動裝置開發"
	"軟體工程師"
	"雲端工程師",
	"系統架構師",
	"數據 / 資料分析師",
	"資料工程 / 機器學習",
	"大數據工程師",
	"AI 工程師"
]

logger.info("🚀 開始發送 %s 個 Yourator 爬蟲任務", len(job_categories))

tasks = []

# 為每個分類創建一個任務
for category in job_categories:

    task = crawl_yourator_jobs.s(category=category)
    task.apply_async(queue="crawler-queue")

    tasks.append(task)
    logger.info("📤 已發送 Yourator 爬蟲任務: %s | ID: %s", category, task.id)

logger.info("✅ 所有 Yourator 爬蟲任務已發送完成，共 %s 個任務", len(tasks))
