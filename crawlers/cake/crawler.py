import urllib.request as req
import json
from typing import cast, List
from bs4 import BeautifulSoup, Tag
from shared.logger import logger
from ..constants import COMMON_SKILLS
from .constants import job_type_dict, salary_type_dict

BASE_URL = "https://www.cake.me"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}


def crawl_cake_jobs_by_category(category):
    result = []
    page = 1
    category_id = category["id"]
    category_name = category["name"]

    logger.info("🐛 開始爬取 Cake 職缺 | %s", category_name)

    while True:
        # if job_type is None then https://www.cake.me/campaigns/software-developer/jobs?page=1
        # if job_type is it_front-end-engineer then
        # https://www.cake.me/campaigns/software-developer/jobs?page=1&profession[0]=it_front-end-engineer

        base_url = f"{BASE_URL}/jobs/categories/it/{category_id}?page={page}"
        url = base_url

        r = req.Request(url)
        r.add_header(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        )

        try:
            res = req.urlopen(r)
        except Exception as e:
            logger.error("請求 %s 失敗 | %s", url, e)
            break

        soup = BeautifulSoup(res.read(), features="html.parser")

        # 型別很嚴格，要先轉型不然 IDE 會報錯
        jobs = cast(
            List[Tag],
            soup.find_all("div", {"class": "JobSearchItem_wrapper__bb_vR"}),
        )

        for job in jobs:
            job_title = cast(Tag, job.select_one("a.JobSearchItem_jobTitle__bu6yO"))

            company_name = _safe_get_text(job, "a.JobSearchItem_companyName__bY7JI")

            # logger.info("🔍 [Cake] | %s | %s", company_name, job_title.text)

            # 這裡的資料不太完整，所以先不使用
            # job_skill_list = job.find_all("div", {"class": "Tags_item__B6Bjo"})
            # ['Golang', 'Java'] > "Golang,Java,"
            # 1. job_skill = "Golang,"
            # 2. job_skill = "Golang,Java,"
            # job_skill = ""
            # for skill in job_skill_list:
            #     job_skill = job_skill + " / " + skill.text

            # job_features 的 index 順序：
            # 0. 全職
            # 1. 大安區, 台北市
            # 2. 100000-150000
            # 3. 1-3年
            job_features = job.select(
                "div.JobSearchItem_features__hR3pk .InlineMessage_inlineMessage____Ulc"
            )

            job_url = f"{BASE_URL}{job_title.get('href')}"
            html = _fetch_job_detail_html(job_url)
            if html == "":
                continue

            job_description = _extract_job_description(html)
            required_skills = _extract_job_skills(html)

            job_data = _get_job_data(html)

            salary_text = _extract_job_salary(job_features)
            salary_min = safe_to_int(job_data["job"].get("salary_min"))
            salary_max = safe_to_int(job_data["job"].get("salary_max"))
            # 預設為 "面議"
            salary_type = (
                salary_type_dict.get(job_data["job"].get("salary_type")) or "面議"
            )
            # 如果完全沒有薪資範圍，強制為面議
            if salary_min is None and salary_max is None:
                salary_type = "面議"

            experience_text = _extract_job_experience(job_features)
            min_work_exp_year = job_data["job"].get("min_work_exp_year")
            experience_min = int(min_work_exp_year) if min_work_exp_year else 0

            work_type = job_type_dict[job_data["job"]["job_type"]]

            city = job_data["company"]["geo_state_name_l"]
            district = job_data["company"]["geo_city_l"]
            location = job_data["company"]["geo_formatted_address_l"]

            data = {
                "job_title": job_title.text,
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
                "category": "軟體／工程類人員",
                "sub_category": category_name,
                "platform": "Cake",
            }
            result.append(data)

        page += 1

    logger.info("🔍 [Cake] | %s | 總共爬取了 %s 個職缺", category_name, len(result))

    return result


def safe_to_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _extract_job_skills(job_detail_html):
    try:
        found_skills = set()
        soup = BeautifulSoup(job_detail_html, features="html.parser")
        job_description_list = soup.find_all(
            "div", {"class": "ContentSection_contentSection__ELRlG"}
        )
        for job_description in job_description_list:
            for line in job_description.stripped_strings:
                line_lower = line.lower()
                for skill in COMMON_SKILLS:
                    if skill.lower() in line_lower:
                        found_skills.add(skill)
        return ",".join(sorted(found_skills)) if found_skills else ""
    except Exception as e:
        logger.error("Failed to parse skills: %s", e)
        return ""


def _extract_job_description(job_detail_html):
    try:
        soup = BeautifulSoup(job_detail_html, features="html.parser")
        job_description_list = soup.find_all(
            "div", {"class": "ContentSection_contentSection__ELRlG"}
        )

        all_text = []

        for job_description in job_description_list:
            text_content = " ".join(job_description.stripped_strings)
            if text_content:
                all_text.append(text_content)

        return " ".join(all_text)
    except Exception as e:
        logger.error("Failed to parse job description: %s", e)
        return ""


def _extract_job_salary(job_features):
    try:
        for feature in job_features:
            if feature.select_one("div.InlineMessage_icon__2M_1k .fa.fa-dollar-sign"):
                return feature.select_one("div.InlineMessage_label__LJGjW").text
    except (IndexError, AttributeError):
        return ""


def _extract_job_experience(job_features):
    try:
        for feature in job_features:
            if feature.select_one("div.InlineMessage_icon__2M_1k .fa.fa-business-time"):
                return feature.select_one("div.InlineMessage_label__LJGjW").text
    except (IndexError, AttributeError):
        return ""


def _fetch_job_detail_html(job_url):
    try:
        r = req.Request(job_url)
        r.add_header(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        )
        res = req.urlopen(r)
        return res.read()
    except Exception as e:
        logger.error("請求 %s 失敗 | %s", job_url, e)
        return ""


def _safe_get_text(soup, selector, default=""):
    try:
        return soup.select_one(selector).text
    except (IndexError, AttributeError):
        return default


def _get_job_data(html):
    soup = BeautifulSoup(html, features="html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        json_data = json.loads(script_tag.string)
        page_props = json_data.get("props", {}).get("pageProps", {})
        return page_props
    return {}
