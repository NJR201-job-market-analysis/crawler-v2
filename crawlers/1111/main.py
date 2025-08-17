from .crawler import crawl_1111_jobs_by_category, crawl_1111_jobs_by_keyword

from shared.files import save_to_csv
from shared.db import Database
from .constants import job_categories

# results = crawl_1111_jobs_by_category({"id": "140607", "name": "雲端工程師"})
# results = crawl_1111_jobs_by_keyword("DevOps")
# print(f"總共爬取了 {len(results)} 個職缺")
# save_to_csv(results, "1111_140802_frontend_engineer")
# Database().insert_jobs(results)

for category in job_categories:
    results = crawl_1111_jobs_by_category(category)
    print(f"總共爬取了 {len(results)} 個職缺")
    Database().insert_jobs(results)
