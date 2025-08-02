from .crawler import crawl_1111_jobs_by_category

# https://www.cake.me/campaigns?locationId=1&page=1

# 測試用
result = crawl_1111_jobs_by_category(category_id="140213")
print(result)
exit()
