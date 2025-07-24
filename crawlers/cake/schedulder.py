from celery.schedules import crontab
from worker import app
from tasks import crawl_cake_jobs


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    設定定時任務
    """
    # 每天早上 9 點執行
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        crawl_cake_jobs.s("software-developer", None, "daily_software_developer"),
        name="daily-software-developer-crawl",
    )

    # 每天晚上 6 點執行
    sender.add_periodic_task(
        crontab(hour=18, minute=0),
        crawl_cake_jobs.s("remote-work", "it", "daily_remote_work"),
        name="daily-remote-work-crawl",
    )
