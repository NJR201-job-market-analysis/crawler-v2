from .crawler import crawl_1111_jobs_by_category
from shared.files import save_to_csv

# https://www.cake.me/campaigns?locationId=1&page=1

# 測試用
results = crawl_1111_jobs_by_category({"id": "140802", "name": "前端工程師"})
print(f"總共爬取了 {len(results)} 個職缺")
save_to_csv(results, "1111_140802_frontend_engineer")
