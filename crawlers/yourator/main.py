from .crawler import crawl_yourator_jobs_by_category
from shared.files import save_to_csv
from shared.db import Database
from .constants import job_categories

for category in job_categories:
    results = crawl_yourator_jobs_by_category(category)
    print(f"總共爬取了 {len(results)} 個職缺")
    # save_to_csv(results, f"yourator_{category}_jobs")
    Database().insert_jobs(results)
