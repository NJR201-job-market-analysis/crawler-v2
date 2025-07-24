import time
import random
import requests
import pandas as pd
from collections import deque
from tqdm import tqdm

class Job104Crawler:
    WEB_NAME = '104人力銀行'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Referer': 'https://www.104.com.tw/jobs/search',
    }

    def __init__(self, keywords="雲端工程師", jobcat_code="2007000000", order=15):
        self.keywords = keywords
        self.jobcat_code = jobcat_code
        self.order = order
        self.timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.file_name = f"({self.timestamp})_{self.WEB_NAME}_{self.keywords}_{self.jobcat_code}"
        self.all_jobs_df = pd.DataFrame()
        self.job_urls = []

    def fetch_jobs_url(self, max_length=4, page_size=30):
        base_url = "https://www.104.com.tw/jobs/search/api/jobs"
        page = 1
        max_page = 10
        recent_counts = deque(maxlen=max_length)
        job_url_set = set()

        with requests.Session() as session, tqdm(total=max_page, desc="104 職缺列表", unit="PAGE", leave=True) as pbar:
            while True:
                params = {
                    'jobsource': 'm_joblist_search',
                    'page': page,
                    'pagesize': page_size,
                    'order': self.order,
                    'jobcat': self.jobcat_code,
                    'keyword': self.keywords,
                }
                try:
                    response = session.get(base_url, headers=self.HEADERS, params=params, timeout=20)
                    response.raise_for_status()
                    api_job_urls = response.json().get('data', [])
                except Exception as e:
                    print(f"API請求失敗 page={page}: {e}, response={getattr(response, 'text', '')[:100]}")
                    break

                for job_url in api_job_urls:
                    job_url_set.add(job_url['link']['job'])

                total_jobs = len(job_url_set)
                recent_counts.append(total_jobs)
                if len(recent_counts) == max_length and len(set(recent_counts)) == 1:
                    print(f"連續{max_length}頁無新資料，結束職缺擷取。")
                    break

                time.sleep(random.uniform(0.5, 1.5))
                pbar.set_postfix_str(f"目前頁面 {page}, 最大頁數: {max_page}")
                pbar.update(1)

                page += 1
                if page >= max_page:
                    max_page = page + 1
                    pbar.total = max_page

        modified_job_url_set = {f"https://www.104.com.tw/job/ajax/content/{url.split('/')[-1]}" for url in job_url_set}
        self.job_urls = list(modified_job_url_set)
        print(f"共獲取到 {len(self.job_urls)} 筆職缺網址。")
        return self.job_urls

    def fetch_job_data(self, job_url):
        try:
            response = requests.get(job_url, headers=self.HEADERS, timeout=20)
            resp_json = response.json()
        except Exception as e:
            print(f"[錯誤] 解析JSON失敗: {job_url}, error={e}, response={getattr(response, 'text', '')[:200]}")
            return pd.DataFrame()
        if 'data' not in resp_json:
            print(f"[警告] API無data欄位: {job_url}, response={resp_json}")
            return pd.DataFrame()
        jobMetaData = resp_json['data']
        df = pd.json_normalize(jobMetaData)
        return df

    def crawl_all_jobs(self):
        print(f"開始執行: {self.file_name}")
        if not self.job_urls:
            self.fetch_jobs_url()
        all_jobs_df = pd.DataFrame()
        for url in tqdm(self.job_urls, desc="Fetching job data", unit="job"):
            df_job_data = self.fetch_job_data(url)
            if not df_job_data.empty:
                all_jobs_df = pd.concat([all_jobs_df, df_job_data], ignore_index=True)
        self.all_jobs_df = all_jobs_df
        print(f"職缺資料擷取完成，共 {len(self.all_jobs_df)} 筆。")
        return self.all_jobs_df

    def save_to_csv(self):
        if self.all_jobs_df.empty:
            print("尚無資料可存檔，請先爬取資料。")
            return
        self.all_jobs_df.to_csv(f"{self.file_name}.csv", encoding='utf-8-sig', index=False)
        print(f"存檔完成 : {self.file_name}.csv")

    def get_columns(self):
        return self.all_jobs_df.columns if not self.all_jobs_df.empty else None

# 使用範例
if __name__ == "__main__":
    crawler = Job104Crawler(keywords="雲端工程師", jobcat_code="2007000000")
    crawler.fetch_jobs_url()
    crawler.crawl_all_jobs()
    crawler.save_to_csv()