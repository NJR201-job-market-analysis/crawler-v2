# crawler

本專案為多網站職缺爬蟲程式集合，支援 104 人力銀行、1111 人力銀行、Cake.me、Yourator 及 LinkedIn 等平台的職缺資料擷取與分析。

## 專案結構

- `104/`
  - `104人力銀行_crawl.ipynb`：104 人力銀行職缺爬蟲與資料分析 Notebook

- `1111/`
  - `新專題main.py`、`新專案main2.py`：1111 人力銀行職缺爬蟲主程式

- `cake/`  
  - `cake_crawler.py`：Cake.me 職缺爬蟲主程式  
  - `main.py`：Cake.me 爬蟲執行入口  
  - `cake_me_crawl_20250523.ipynb`：Cake.me 職缺資料分析與爬取範例 Notebook

- `yourator/`  
  - `yourator_crawler.py`：Yourator 職缺爬蟲主程式  
  - `main.py`：Yourator 爬蟲執行入口

- `linkedin/`
  - `linkedin.py`：LinkedIn 職缺爬蟲主程式
  - `Linkedin_crawl_20250527.ipynb`：LinkedIn 職缺爬蟲與資料分析 Notebook

## 使用方式

1. 進入對應資料夾（如 `104/`、`1111/`、`cake/`、`yourator/` 或 `linkedin/`）。
2. 執行 `main.py`、相關 Python 檔案或 Notebook 以開始爬取職缺資料，結果將輸出為 CSV 檔案。
3. 亦可參考 Notebook 進行進階資料分析。

## 依賴套件

- requests
- beautifulsoup4
- pandas
- tqdm（主要用於 Notebook）
- selenium（LinkedIn 爬蟲需要）

請先安裝相關 Python 套件。

## 版權

僅供學術與技術交流使用，請勿用於商業用途。