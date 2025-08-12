from .crawler import crawl_yourator_jobs_by_category
from shared.files import save_to_csv

results = crawl_yourator_jobs_by_category("前端工程")
print(f"總共爬取了 {len(results)} 個職缺")
save_to_csv(results, "yourator_frontend_jobs")
