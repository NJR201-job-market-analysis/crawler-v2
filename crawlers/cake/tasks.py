from datetime import datetime
from shared.logger import logger
from shared.db import Database
from crawlers.worker import app
from .crawler import crawl_cake_jobs_by_category


@app.task(bind=True)
def crawl_cake_jobs(self, category, job_type):

    task_id = self.request.id
    start_time = datetime.now()

    try:
        result = crawl_cake_jobs_by_category(category, job_type)

        logger.info(
            "🗄️  寫入資料庫 | 📂 %s | 🏷️  %s | 📊 %s 筆",
            category,
            job_type,
            len(result),
        )
        Database().insert_jobs(result)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("✅ 任務完成 %s | 耗時: %.2f秒", task_id, duration)

        return {
            "status": "success",
            "task_id": task_id,
            "category": category,
            "job_type": job_type,
            "duration": duration,
            "result_count": len(result),
            "timestamp": end_time.isoformat(),
        }
    except Exception as e:
        logger.error("❌ 任務失敗 %s | 錯誤: %s", task_id, str(e))

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "status": "error",
            "task_id": task_id,
            "error": str(e),
            "category": category,
            "job_type": job_type,
            "duration": duration,
            "timestamp": end_time.isoformat(),
        }


@app.task
def test_task():
    """
    Simple test task
    """
    return "Hello from Cake worker!"
