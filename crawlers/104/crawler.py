import urllib.request as req
import json
import re
import time
import random
from shared.logger import logger
from .constants import job_type_dict, salary_type_dict
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
        job_list_res = fetch_job_list(category_id, page)
        if job_list_res is None:
            logger.info("請求 category:%s, page:%s 失敗", category_name, page)
            break

        last_page = job_list_res["metadata"]["pagination"]["lastPage"]

        for tmp in job_list_res["data"]:
            job_url = tmp["link"]["job"]
            job_id = job_url.split("/")[-1]

            logger.info(
                "🔍 [104] | %s | %s | %s", tmp["custName"], tmp["jobName"], job_id
            )

            job_res = fetch_job_detail(job_id)

            if job_res is None:
                logger.info(
                    "❌ [104] 未成功取得職缺 | %s | %s",
                    tmp["custName"],
                    tmp["jobName"],
                )
                continue
            job = job_res["data"]
            if job is None:
                logger.info(
                    "❌ [104] 未成功取得職缺 | %s | %s",
                    tmp["custName"],
                    tmp["jobName"],
                )
                continue

            job_detail = job["jobDetail"]

            company_name = job["header"]["custName"]
            job_title = job["header"]["jobName"]
            job_description = job_detail["jobDescription"]
            required_skills = extract_skills(job_description)

            city = job_detail["addressArea"]
            district = job_detail["addressRegion"].replace(city, "")
            location = f"{job_detail['addressRegion']}{job_detail['addressDetail']}"

            work_type = job_type_dict[job_detail["jobType"]]

            salary_text = job_detail["salary"] or ""
            salary_min = (
                job_detail["salaryMin"] if job_detail["salaryMin"] != 0 else None
            )
            salary_max = (
                job_detail["salaryMax"]
                if job_detail["salaryMax"] != 9999999 and job_detail["salaryMax"] != 0
                else None
            )
            salary_type = salary_type_dict.get(job_detail["salaryType"]) or "negotiable"

            experience_text = job["condition"]["workExp"] or ""
            experience_min = ""
            if experience_text == "不拘":
                experience_min = 0
            else:
                match = re.search(r"\d+", experience_text)
                if match:
                    experience_min = int(match.group())
                else:
                    experience_min = None

            data = {
                "job_title": job_title,
                "company_name": company_name,
                "work_type": work_type,
                "required_skills": required_skills,
                "job_description": job_description,
                "salary_text": salary_text,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_type": salary_type,
                "experience_text": experience_text,
                "experience_min": experience_min,
                "city": city,
                "district": district,
                "location": location,
                "job_url": job_url,
                "category": "軟體 / 工程類人員",
                "sub_category": category_name,
                "platform": "104",
            }
            result.append(data)

            time.sleep(random.uniform(0.5, 1.5))

        page += 1

        if page > last_page:
            break

    logger.info("🔍 [104] | %s | 總共爬取了 %s 個職缺", category_name, len(result))

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
