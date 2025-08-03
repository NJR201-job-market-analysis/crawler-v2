import urllib.request as req
import json

# from typing import cast, List
# from bs4 import BeautifulSoup, Tag
from shared.logger import logger

# from shared.files import save_to_csv
from .constants import job_type_dict
from ..constants import COMMON_SKILLS

# https://www.104.com.tw/jobs/search/api/jobs?jobcat=2007000000&jobsource=index_s&mode=s&page=1&pagesize=20
BASE_URL = "https://www.104.com.tw/jobs/search/api/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "Referer": "https://www.104.com.tw/jobs/search",
}


def crawl_104_jobs_by_category(category):
    result = []
    page = 1
    category_id = category["id"]
    category_name = category["name"]

    logger.info("🐛 開始爬取 104 職缺 | %s | %s", category_id, category_name)

    while True:
        json = fetch_job_list(category_id, page)
        if json is None:
            logger.info("請求 category:%s, page:%s 失敗", category_name, page)
            break

        last_page = json["metadata"]["pagination"]["lastPage"]
        if page == last_page:
            break

        for tmp in json["data"]:
            job_url = tmp["link"]["job"]
            job_id = job_url.split("/")[-1]

            logger.info(
                "🔍 [104] | %s | %s | %s", tmp["custName"], tmp["jobName"], job_id
            )

            job = fetch_job_detail(job_id)["data"]

            if job is None:
                logger.info(
                    "❌ [104] | %s | %s",
                    tmp["custName"],
                    tmp["jobName"],
                )
                continue

            job_company_name = job["header"]["custName"]
            job_title = job["header"]["jobName"]
            job_description = job["jobDetail"]["jobDescription"]
            job_location = job["jobDetail"]["addressRegion"]
            job_work_type = job_type_dict[job["jobDetail"]["jobType"]]
            job_salary = (
                job["jobDetail"]["salary"] if job["jobDetail"]["salary"] else ""
            )
            job_exp = job["condition"]["workExp"]

            job_category = []
            for category in job["jobDetail"]["jobCategory"]:
                job_category.append(category["description"])
            job_category = ";".join(job_category)

            job_skill = extract_skills(job_description)

            data = {
                "job_title": job_title,
                "job_url": job_url,
                "job_type": "",
                "company_name": job_company_name,
                "work_type": job_work_type,
                "required_skills": job_skill,
                "job_description": job_description,
                "location": job_location,
                "salary": job_salary,
                "experience": job_exp,
                "category": "軟體 / 工程類人員",
                "sub_category": category_name,
                "platform": "104",
            }
            result.append(data)

        page += 1

    # save_to_csv(result, f"104_jobs_{category_name}")

    return result


def safe_parse_json(res):
    try:
        data = res.read()
        json_str = data.decode("utf-8")
        json_data = json.loads(json_str)
        return json_data
    except Exception as e:
        logger.error("解析 JSON 失敗 | %s", e)
        return None


def extract_skills(job_description):
    found_skills = set()
    for skill in COMMON_SKILLS:
        if skill.lower() in job_description.lower():
            found_skills.add(skill)
    return ",".join(sorted(found_skills)) if found_skills else ""


def fetch_job_list(category_id, page):
    try:
        request_url = f"{BASE_URL}?jobcat={category_id}&jobsource=index_s&mode=s&page={page}&pagesize=20"
        r = req.Request(request_url)
        r.add_header("User-Agent", HEADERS["User-Agent"])
        r.add_header("Referer", HEADERS["Referer"])
        res = req.urlopen(r)
        return safe_parse_json(res)
    except Exception as e:
        logger.error("請求 %s 失敗 | %s", request_url, e)
        return None


def fetch_job_detail(job_id):
    job_url = f"https://www.104.com.tw/job/ajax/content/{job_id}"
    r = req.Request(job_url)
    r.add_header("User-Agent", HEADERS["User-Agent"])
    r.add_header("Referer", HEADERS["Referer"])
    try:
        res = req.urlopen(r)
        return safe_parse_json(res)
    except Exception as e:
        logger.error("請求 %s 失敗 | %s", job_url, e)
        return None
