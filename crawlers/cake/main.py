from crawler import crawl_cake_jobs_by_category

# https://www.cake.me/campaigns?locationId=1&page=1

# 測試用
result = crawl_cake_jobs_by_category("top500-companies", "it")
# CakeDatabase().insert_jobs(result)
# cake_crawler("software-developer", None, "cakesoftwaredeveloperjobs")
# cake_crawler("digital-nomad", "it", "cakedigitalnomadjobs")

