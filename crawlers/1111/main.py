from .crawler import crawl_1111_jobs_by_category

# from shared.files import save_to_csv
from shared.db import Database
from .constants import job_categories

# https://www.cake.me/campaigns?locationId=1&page=1

# results = crawl_1111_jobs_by_category({"id": "140802", "name": "前端工程師"})
# print(f"總共爬取了 {len(results)} 個職缺")
# save_to_csv(results, "1111_140802_frontend_engineer")
# Database().insert_jobs(results)

for category in job_categories:
    results = crawl_1111_jobs_by_category(category)
    print(f"總共爬取了 {len(results)} 個職缺")
    Database().insert_jobs(results)
