from .crawler import crawl_cake_jobs_by_category
from shared.files import save_to_csv
from shared.db import Database

# https://www.cake.me/campaigns?locationId=1&page=1

# 測試用
results = crawl_cake_jobs_by_category(
    {"id": "front-end-engineer", "name": "前端工程師"}
)
print(f"總共爬取了 {len(results)} 個職缺")
# save_to_csv(results, "cake_frontend_engineer")
Database().insert_jobs(results)
# cake_crawler("software-developer", None, "cakesoftwaredeveloperjobs")
# cake_crawler("digital-nomad", "it", "cakedigitalnomadjobs")
