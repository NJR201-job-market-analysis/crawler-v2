import urllib.request as req
import bs4 as bs
import re
import urllib
import ssl
import json
from shared.logger import logger
from ..constants import COMMON_SKILLS

# https://www.1111.com.tw/api/v1/search/jobs/?page=1&fromOffset=2&jobPositions=140600"
BASE_URL = "https://www.1111.com.tw/api/v1/search/jobs/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}

# 直接爬會跳出ssl認證沒過, ssl這行是google來的指令 貼上去後才可以爬取
ssl._create_default_https_context = ssl._create_unverified_context


def analaze_pages(url):
    r = req.Request(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        },
    )
    resp = req.urlopen(r)
    content = resp.read().decode("utf-8")
    html = bs.BeautifulSoup(content, "html.parser")

    job_description = html.find("div", {"class": "whitespace-pre-line"}).text
    # skills = html.find_all("p", {"class": "underline-offset-1"})
    # 電腦專長(前面是電腦專長list, list最後一項卻是抓出公司名稱, 所以pop掉.
    # 但如果廣告沒有刊登電腦專長, 一樣會抓到公司名稱, 所以沿用pop後變成的空集合, 賦值"沒有刊登電腦專長"
    # skill_list = []
    # for skill in skills:
    #     skill_list.append(skill.text)
    # skill_list.pop()
    # if skill_list == []:
    #     skill_list = "沒有刊登電腦專長"

    # 地址的標頭和"class"有兩種...#爬出來的地址會參雜一堆空格和換行, 這裡先設一個空list,
    # 再用for in回圈寫入有意義的文字(空格和換行符號不寫入)
    work_place = html.find("p", {"class": "mb-4"})  # 第一種路徑
    if work_place == None:  # 如果第一種路徑抓不到
        work_place = html.find(
            "div", {"class": "md:items-center content"}
        ).p.text  # 就它了
        work_place_location = ""
        for w in work_place:
            if w == " " or w == "\n":
                continue
        else:
            work_place_location = work_place_location + w
    else:
        work_place_location = ""
        for s in work_place.text:
            if s == " " or s == "\n":
                continue  # 不寫入空格" "和換行符號"\n" 遇到就回前面, 不執行append(a)
            work_place_location = work_place_location + s

    # 遠端 有的公司直接缺少該欄位 用class會撈到別的東西 所以查找關鍵字"遠端上班"的"遠"
    # (不用"端"是因為會撈出前端後端)(應該有更好的解法, 待我再研究XD)
    contents = html.find_all("div", {"class": "content"})

    work_type = "全職"
    experience_text = ""
    # job_category = ""
    salary_text = ""
    city = ""
    district = ""
    location = ""
    required_skills = set()
    # 先從職缺描述中提取技能
    required_skills.update(_extract_job_skills_from_job_description(job_description))

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
                required_skills.update(_extract_job_skills_from_computer_field(content))
            if content.h3.text == "附加條件":
                required_skills.update(
                    _extract_job_skills_from_additional_field(content)
                )
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

    # 日薪 3,500元~4,500元
    # 日薪 2,500元以上
    salary_min = ""
    salary_max = ""
    salary_type = ""
    if "面議" in salary_text:
        salary_max = None
        salary_min = None
        salary_type = "面議"
    else:
        salary_min, salary_max = _extract_salary_range(salary_text)
        for keyword in ["月薪", "年薪", "日薪", "時薪", "論件計酬"]:
            if keyword in salary_text:
                salary_type = keyword
                break

    experience_min = ""
    if experience_text == "不拘":
        experience_min = 0
    else:
        match = re.search(r"\d+", experience_text)
        if match:
            experience_min = int(match.group())
        else:
            experience_min = None

    # 出差
    # for job_trip in contents:
    #     if job_trip.h3 != None:
    #         if job_trip.h3 == "其他說明":
    #             job_trips = job_trip.p.text
    #         else:
    #             job_trips = "不用出差"

    # 更新時間
    updata_time = html.find("span", {"class": "leading-[1.8] text-[16px]"}).text

    data = {
        "job_description": job_description,
        "required_skills": ",".join(sorted(required_skills)) if required_skills else "",
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
        "update_time": updata_time,
    }
    return data


def crawl_1111_jobs_by_category(category):
    result = []
    page = 1

    category_id = category["id"]
    category_name = category["name"]

    logger.info("🐛 開始爬取 1111 職缺 | %s | %s", category_id, category_name)

    while True:
        json = fetch_job_list(category_id, page)
        if json is None:
            logger.info("請求 category:%s, page:%s 失敗", category_name, page)
            break

        total_page = json["result"]["pagination"]["totalPage"]

        for job in json["result"]["hits"]:
            job_id = job["jobId"]
            job_title = job["title"]
            # job_location = job["workCity"]["name"]
            company_name = job["companyName"]

            logger.info("🔍 [1111] | %s | %s | %s", company_name, job_title, job_id)

            job_url = f"https://www.1111.com.tw/job/{job_id}"
            job_detail = analaze_pages(job_url)

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
                "category": "軟體 / 工程類人員",
                "sub_category": category_name,
                "platform": "1111",
            }
            result.append(data)

        page += 1

        if page > total_page:
            break

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


def fetch_job_list(category_id, page):
    try:
        request_url = f"{BASE_URL}?page={page}&sort=desc&jobPositions={category_id}"
        r = req.Request(request_url)
        r.add_header("User-Agent", HEADERS["User-Agent"])
        res = req.urlopen(r)
        return safe_parse_json(res)
    except Exception as e:
        logger.error("請求 %s 失敗 | %s", request_url, e)
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


def _extract_salary_range(salary_str):
    numbers = re.findall(r"\d{1,3}(?:,\d{3})*", salary_str)
    numbers = [int(num.replace(",", "")) for num in numbers]

    if len(numbers) == 1:
        return numbers[0], None
    elif len(numbers) >= 2:
        return numbers[0], numbers[1]
    else:
        return None, None
