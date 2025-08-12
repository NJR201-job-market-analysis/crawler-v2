import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
from shared.logger import logger
from .constants import job_salary_type_dict
from ..constants import (
    COMMON_SKILLS,
    EXPERIENCE_KEYWORDS_SIMPLE,
    job_category_mapping,
)
from ..utils import extract_salary_range, extract_experience_min


BASE_URL = "https://www.yourator.co"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}


# 取得職缺列表
def fetch_job_list(page, category):
    url = f"{BASE_URL}/api/v4/jobs?category[]={quote(category)}&page={page}"
    print(f"Fetching job list: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch job list: {e}")
        return None


# 取得職缺詳細資訊的 html
def fetch_job_html(job_url):
    try:
        resp = requests.get(job_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Failed to fetch job detail: {e}")
        return ""


# 取得職缺詳細資訊的經驗
def extract_job_experience(soup):
    try:
        texts = soup.stripped_strings
        for line in texts:
            for keyword in EXPERIENCE_KEYWORDS_SIMPLE:
                if keyword in line:
                    return line
        return "不限"
    except Exception as e:
        print(f"Failed to fetch job detail: {e}")
        return ""


def extract_job_description(soup):
    content = soup.select_one("div.job__content")
    if content:
        return content.get_text(strip=True, separator="\n")
    return ""


# 取得職缺詳細資訊的技能
def extract_job_skills(soup):
    try:
        found_skills = set()
        for line in soup.stripped_strings:
            line_lower = line.lower()
            for skill in COMMON_SKILLS:
                if skill.lower() in line_lower:
                    found_skills.add(skill)
        return found_skills
    except Exception as e:
        print(f"Failed to parse skills: {e}")
        return ""


def crawl_yourator_jobs_by_category(category):
    results = []
    page = 1
    while True:
        job_list_res = fetch_job_list(page, category)
        if not job_list_res or not job_list_res["payload"]["jobs"]:
            break

        for job in job_list_res["payload"]["jobs"]:
            job_url = BASE_URL + job["path"]
            job_title = job["name"]
            company_name = job["company"]["brand"]

            logger.info("🔍 [Yourator] | %s | %s", company_name, job_title)

            html = fetch_job_html(job_url)
            soup = BeautifulSoup(html, "html.parser")

            work_type = soup.select_one(".basic-info__job_type").get_text(strip=True)
            job_description = extract_job_description(soup)

            skills = extract_job_skills(soup)
            raw_skills = ",".join(sorted(skills)) if skills else ""

            experience_text = extract_job_experience(soup)
            experience_min = extract_experience_min(experience_text)

            categories = [job_category_mapping.get(category)]

            salary_text = job["salary"]
            salary_min, salary_max = extract_salary_range(salary_text)
            salary_type = ""
            if any(keyword in salary_text for keyword in ["Negotiable", "面議"]):
                salary_min = 40000
                salary_max = None
                salary_type = "面議"
            else:
                for keyword in ["Annual", "Monthly", "Hourly", "piecework"]:
                    if keyword in salary_text:
                        salary_type = job_salary_type_dict[keyword]
                        break

            city = job["location"]
            district = ""
            location_el = soup.select_one(".basic-info__address")
            location = location_el.get_text(strip=True) if location_el else None

            results.append(
                {
                    "job_title": job_title,
                    "company_name": company_name,
                    "work_type": work_type,
                    "required_skills": raw_skills,
                    "job_description": job_description,
                    "salary_text": salary_text,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_type": salary_type,
                    "experience_text": experience_text,
                    "experience_min": experience_min,
                    "job_url": job_url,
                    "city": city,
                    "district": district,
                    "location": location,
                    "platform": "Yourator",
                    "skills": list(skills),
                    "categories": categories,
                }
            )
            time.sleep(1)
        if not job_list_res["payload"]["hasMore"]:
            break
        page += 1

    return results
