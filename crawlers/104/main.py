from .crawler import crawl_104_jobs_by_category

# 直接調用爬蟲函數，不使用分散式架構
if __name__ == "__main__":
    category_id = "2007001015"
    results = crawl_104_jobs_by_category(category_id)

    print(f"總共爬取了 {len(results)} 個職缺")
