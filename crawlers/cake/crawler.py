import urllib.request as req
from typing import cast, List
from bs4 import BeautifulSoup, Tag

from shared.logger import logger
# from shared.files import save_to_csv
from ..constants import COMMON_SKILLS

BASE_URL = "https://www.cake.me"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}


def crawl_cake_jobs_by_category(category):
    result = []
    page = 1
    category_id = category["id"]
    category_name = category["name"]

    logger.info("🐛 開始爬取 Cake %s 職缺", category_name)

    while True:
        # if job_type is None then https://www.cake.me/campaigns/software-developer/jobs?page=1
        # if job_type is it_front-end-engineer then
        # https://www.cake.me/campaigns/software-developer/jobs?page=1&profession[0]=it_front-end-engineer

        base_url = f"{BASE_URL}/jobs/categories/it/{category_id}?page={page}"
        url = base_url

        # print("頁面:", url)

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
            soup.find_all("div", {"class": "CampaignJobSearchItem_wrapper__HsxKW"}),
        )

        for job in jobs:
            job_title = cast(
                Tag, job.select_one("a.CampaignJobSearchItem_jobTitle__LQGW_")
            )

            company_name = _safe_get_text(
                job, "a.CampaignJobSearchItem_companyName__i9OXl"
            )

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
                "div.CampaignJobSearchItem_features__H3moX .InlineMessage_inlineMessage____Ulc"
            )

            # 工作類型 (全職、兼職、實習)
            job_work_type = _safe_get_job_work_type(job_features)
            job_location = _safe_get_job_location(job_features)
            job_salary = _safe_get_job_salary(job_features)
            job_exp = _safe_get_job_experience(job_features)
            job_url = f"{BASE_URL}{job_title.get('href')}"
            job_detail_html = _fetch_job_detail(job_url)
            job_description = _extract_job_description(job_detail_html)
            job_skill = _extract_skills(job_detail_html)

            data = {
                "job_title": job_title.text,
                "company_name": company_name,
                "work_type": job_work_type,
                "required_skills": job_skill,
                "job_description": job_description,
                "location": job_location,
                "salary": job_salary,
                "experience": job_exp,
                "job_url": job_url,
                "category": "軟體／工程類人員",
                "sub_category": category_name,
                "platform": "Cake",
            }
            result.append(data)

        page += 1

    # save_to_csv(result, f"cake_jobs_{category}_{job_type}")

    return result


def _extract_skills(job_detail_html):
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


def _fetch_job_detail(job_url):
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


def _safe_get_job_work_type(job_features):
    try:
        for feature in job_features:
            if feature.select_one("div.InlineMessage_icon__2M_1k .fa.fa-user"):
                return feature.select_one(
                    "div.CampaignJobSearchItem_featureSegments___NcD4 > div:first-child > button"
                ).text
    except (IndexError, AttributeError):
        return ""


def _safe_get_job_location(job_features):
    try:
        for feature in job_features:
            if feature.select_one(
                "div.InlineMessage_icon__2M_1k .fa.fa-map-marker-alt"
            ):
                return feature.select_one(
                    "div.CampaignJobSearchItem_featureSegments___NcD4 span"
                ).text
    except (IndexError, AttributeError):
        return ""


def _safe_get_job_salary(job_features):
    try:
        for feature in job_features:
            if feature.select_one("div.InlineMessage_icon__2M_1k .fa.fa-dollar-sign"):
                return feature.select_one("div.InlineMessage_label__LJGjW").text
    except (IndexError, AttributeError):
        return ""


def _safe_get_job_experience(job_features):
    try:
        for feature in job_features:
            if feature.select_one("div.InlineMessage_icon__2M_1k .fa.fa-business-time"):
                return feature.select_one("div.InlineMessage_label__LJGjW").text
    except (IndexError, AttributeError):
        return ""

