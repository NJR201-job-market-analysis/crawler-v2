from .crawler import crawl_cake_jobs_by_category

# from shared.files import save_to_csv
from shared.db import Database
from .constants import job_categories

# https://www.cake.me/campaigns?locationId=1&page=1

# results = crawl_cake_jobs_by_category(
#     {"id": "front-end-engineer", "name": "前端工程師"}
# )
# print(f"總共爬取了 {len(results)} 個職缺")
# save_to_csv(results, "cake_frontend_engineer")
# Database().insert_jobs(results)

for category in job_categories:
    results = crawl_cake_jobs_by_category(category)
    print(f"總共爬取了 {len(results)} 個職缺")
    Database().insert_jobs(results)
