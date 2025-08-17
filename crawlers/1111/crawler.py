import urllib.request as req
import bs4 as bs
import ssl
import json
from datetime import datetime
from shared.logger import logger
from ..constants import COMMON_SKILLS, job_category_mapping
from ..utils import extract_salary_range, extract_experience_min

# https://www.1111.com.tw/api/v1/search/jobs/?page=1&fromOffset=2&jobPositions=140600"
BASE_URL = "https://www.1111.com.tw/api/v1/search/jobs/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}

# 直接爬會跳出ssl認證沒過, ssl這行是google來的指令 貼上去後才可以爬取
ssl._create_default_https_context = ssl._create_unverified_context


def get_job_detail(url):
    try:
        r = req.Request(
            url,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
            },
        )
        resp = req.urlopen(r)
        content = resp.read().decode("utf-8")
        html = bs.BeautifulSoup(content, "html.parser")
    except Exception as e:
        logger.error("解析職缺描述失敗 | %s", e)
        return None

    job_description_element = html.find("div", {"class": "whitespace-pre-line"})
    job_description = job_description_element.text if job_description_element else ""

    contents = html.find_all("div", {"class": "content"})

    work_type = "全職"
    experience_text = ""
    # job_category = ""
    salary_text = ""
    city = ""
    district = ""
    location = ""
    categories = []
    skills = set()
    # 先從職缺描述中提取技能
    skills.update(_extract_job_skills_from_job_description(job_description))

    for content in contents:
        if content.h3 != None:
            if content.h3.text == "工作經驗":
                # print("工作經驗", content.p.text)
                experience_text = content.p.text
            # if content.h3.text == "職務類別":
            #     job_category = ";".join(content.p.text.split("、"))
            if content.h3.text == "工作待遇":
                salary_text = (
                    next(content.select_one("div.text-main").stripped_strings, "")
                    # .replace("(經常性薪資達4萬元或以上)", "")
                    # .replace("(固定或變動薪資因個人資歷或績效而異)", "")
                )
            if content.h3.text == "電腦專長":
                skills.update(_extract_job_skills_from_computer_field(content))
            if content.h3.text == "附加條件":
                skills.update(_extract_job_skills_from_additional_field(content))
            if content.h3.text == "工作性質":
                work_type_text = content.ul.get_text(strip=True)
                for type_ in ["全職", "兼職", "工讀"]:
                    if type_ in work_type_text:
                        work_type = type_
                        break
            if content.h3.text == "工作地點":
                location_text = content.p.text
                parts = " ".join(location_text.split()).split()
                city = parts[0] if len(parts) > 0 else None
                district = parts[1] if len(parts) > 1 else None
                location = "".join(parts[:3]) if len(parts) >= 2 else None
            if content.h3.text == "工作技能" and job_description == "":
                job_description = content.ul.get_text(strip=True) if content.ul else ""
            if content.h3.text == "職務類別":
                for category in content.select("ul li p"):
                    if category.text in job_category_mapping:
                        categories.append(job_category_mapping[category.text])
                    else:
                        logger.info(f"未對應的 1111 職務類別: {category.text}")

    # 日薪 3,500元~4,500元
    # 日薪 2,500元以上
    salary_min = ""
    salary_max = ""
    salary_type = ""
    if "面議" in salary_text:
        salary_min = 40000
        salary_max = None
        salary_type = "面議"
    else:
        salary_min, salary_max = extract_salary_range(salary_text)
        for keyword in ["月薪", "年薪", "日薪", "時薪", "論件計酬"]:
            if keyword in salary_text:
                salary_type = keyword
                break

    experience_min = extract_experience_min(experience_text)

    raw_skills = ",".join(sorted(skills)) if skills else ""

    data = {
        "job_description": job_description,
        "required_skills": raw_skills,
        "experience_text": experience_text,
        "experience_min": experience_min,
        "work_type": work_type,
        "salary_text": salary_text,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_type": salary_type,
        "city": city,
        "district": district,
        "location": location,
        "skills": list(skills),
        "categories": list(set(categories)),
    }
    return data


def crawl_1111_jobs_by_keyword(keyword):
    logger.info("🐛 開始爬取 1111 職缺 | %s", keyword)

    result = crawl_1111_jobs(f"{BASE_URL}?sort=desc&keyword={keyword}")

    logger.info("🔍 [1111] | %s | 總共爬取了 %s 個職缺", keyword, len(result))

    return result


def crawl_1111_jobs_by_category(category):
    category_id = category["id"]
    category_name = category["name"]

    logger.info("🐛 開始爬取 1111 職缺 | %s | %s", category_id, category_name)
    result = crawl_1111_jobs(f"{BASE_URL}?sort=desc&jobPositions={category_id}")

    logger.info("🔍 [1111] | %s | 總共爬取了 %s 個職缺", category_name, len(result))

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


def crawl_1111_jobs(url):
    result = []
    page = 1

    while True:
        request_url = f"{url}&page={page}"
        job_list_res = fetch_job_list(request_url)
        if job_list_res is None:
            logger.info("請求 %s 失敗", url)
            break

        total_page = job_list_res["result"]["pagination"]["totalPage"]

        for job in job_list_res["result"]["hits"]:
            job_id = job["jobId"]
            job_title = job["title"]
            company_name = job["companyName"]

            logger.info("🔍 [1111] | %s | %s | %s", company_name, job_title, job_id)

            job_url = f"https://www.1111.com.tw/job/{job_id}"
            job_detail = get_job_detail(job_url)

            if job_detail is None:
                logger.info("❌ [1111] | %s | %s", company_name, job_title)
                continue

            data = {
                "job_title": job_title,
                "company_name": company_name,
                "work_type": job_detail["work_type"],
                "required_skills": job_detail["required_skills"],
                "job_description": job_detail["job_description"],
                "salary_text": job_detail["salary_text"],
                "salary_min": job_detail["salary_min"],
                "salary_max": job_detail["salary_max"],
                "salary_type": job_detail["salary_type"],
                "experience_text": job_detail["experience_text"],
                "experience_min": job_detail["experience_min"],
                "city": job_detail["city"],
                "district": job_detail["district"],
                "location": job_detail["location"],
                "job_url": job_url,
                "platform": "1111",
                "skills": job_detail["skills"],
                "categories": job_detail["categories"],
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            result.append(data)

        page += 1

        if page > total_page:
            break

    return result


def fetch_job_list(url):
    try:
        r = req.Request(url)
        r.add_header("User-Agent", HEADERS["User-Agent"])
        res = req.urlopen(r)
        return safe_parse_json(res)
    except Exception as e:
        logger.error("請求 %s 失敗 | %s", url, e)
        return None


def _extract_job_skills_from_job_description(description):
    try:
        description = description.lower()
        found_skills = set()
        for skill in COMMON_SKILLS:
            if skill.lower() in description:
                found_skills.add(skill)
        return found_skills
    except Exception as e:
        logger.error("解析職缺描述失敗 | %s", e)
        return ""


def _extract_job_skills_from_computer_field(soup):
    try:
        found_skills = set()
        for job_skill in soup.select("li > a > p"):
            for skill in COMMON_SKILLS:
                if skill.lower() in job_skill.text.lower():
                    found_skills.add(skill)
        return found_skills
    except Exception as e:
        logger.error("解析電腦專長失敗 | %s", e)
        return ""


def _extract_job_skills_from_additional_field(soup):
    try:
        found_skills = set()
        additional_content_text = soup.select_one("div > div > p").text.lower()
        for skill in COMMON_SKILLS:
            if skill.lower() in additional_content_text:
                found_skills.add(skill)
        return found_skills
    except Exception as e:
        logger.error("解析附加條件失敗 | %s", e)
        return ""
