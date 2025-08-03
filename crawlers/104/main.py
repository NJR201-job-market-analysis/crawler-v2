from .crawler import crawl_104_jobs_by_category
from shared.files import save_to_csv

# 直接調用爬蟲函數，不使用分散式架構
if __name__ == "__main__":
    results = crawl_104_jobs_by_category({"id": "2007001015", "name": "前端工程師"})

    print(f"總共爬取了 {len(results)} 個職缺")
    save_to_csv(results, "104_2007001015_frontend_engineer")
