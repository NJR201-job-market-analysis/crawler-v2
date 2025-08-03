import urllib.request as req
import bs4 as bs
import urllib
import ssl
import json
from shared.logger import logger

# from shared.files import save_to_csv
from ..constants import COMMON_SKILLS

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

    keywords = {
        "遠",
    }
    work_type = set()
    for w in contents:
        if w.h3 != None:
            for keyword in w.h3.text:
                if keyword in keywords:
                    work_type.add(w.h3.text)
        if w.p != None:
            for keyword in w.p.text:
                if keyword in keywords:
                    work_type.add(w.p.text)
    if work_type == set():  # QQ共用的太多了, 一直重複查找, 先用set()刪掉重複抓到的
        work_type = "沒有遠距"
    else:
        work_type = ",".join(work_type)
        if work_type == "發展遠景":
            work_type = "沒有遠距"

    job_experience = ""
    job_category = ""
    job_salary = ""
    job_skills = set()
    # 先從職缺描述中提取技能
    job_skills.update(_extract_job_skills_from_job_description(job_description))

    for content in contents:
        if content.h3 != None:
            if content.h3.text == "工作經驗":
                # print("工作經驗", content.p.text)
                job_experience = content.p.text
            if content.h3.text == "職務類別":
                job_category = ";".join(content.p.text.split("、"))
            if content.h3.text == "工作待遇":
                job_salary = (
                    next(content.select_one("div.text-main").stripped_strings, "")
                    .replace("(經常性薪資達4萬元或以上)", "")
                    .replace("(固定或變動薪資因個人資歷或績效而異)", "")
                )
            if content.h3.text == "電腦專長":
                job_skills.update(_extract_job_skills_from_computer_field(content))
            if content.h3.text == "附加條件":
                job_skills.update(_extract_job_skills_from_additional_field(content))

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
        "description": job_description,
        "skills": ",".join(sorted(job_skills)) if job_skills else "",
        "experience": job_experience,
        "work_type": work_type,
        # "其他說明": job_trips,
        "salary": job_salary,
        "update_time": updata_time,
        "category": job_category,
    }
    return data


# 查找的關鍵字 中間用+連接 ex.software+engineer
looking_for = urllib.parse.quote("軟體+工程師")
looking_for = "desc&ks=" + urllib.parse.quote("軟體+工程師")  # 中文關鍵字
p_start = 1  # 從第幾頁開始找
p_limit = 2  # 找到第幾頁
wfh = False  # 預設不設條件. 但只想找遠端工作, 改成True
ex = False  # 預設不設條件. 但要找工作經驗"不拘"的, 改成False
w_place = []  # 預設不限, 若要特定的縣市, 輸入"兩個字", 並以逗號相隔 ex.["台北","桃園"]
table = []  # 這是張無關緊要的桌子


def find_all_pages(looking_for, p_start, p_limit, w_place, wfh, ex):
    for i in range(p_start, p_limit + 1):
        url = f"https://www.1111.com.tw/search/job?page={i}&col=ab&sort=desc&ks={looking_for}"
        r = req.Request(
            url,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
            },
        )
        resp = req.urlopen(r)
        content = resp.read().decode("utf-8")
        html = bs.BeautifulSoup(content, "html.parser")
        job_list = html.find_all("div", {"class": "shrink-0"})
        for h in job_list:
            if h.find("a", {"class": "mb-1"}) != None:
                job_url = (
                    "https://www.1111.com.tw" + h.find("a", {"class": "mb-1"})["href"]
                )
                # print(job_url)
                # print("-"*10)
                data = analaze_pages(job_url)
                if wfh == True and data["遠距工作"] == "沒有遠距":
                    continue
                if ex == True and data["工作經驗"] != "不拘":
                    continue
                if w_place != [] and data["工作地點"][0:2] not in w_place:
                    continue
                table.append(data)
    return table


# https://www.1111.com.tw/api/v1/search/jobs/?page=1&fromOffset=2&jobPositions=140600"
BASE_URL = "https://www.1111.com.tw/api/v1/search/jobs/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}


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
        if page == total_page:
            break

        for job in json["result"]["hits"]:
            job_id = job["jobId"]
            job_title = job["title"]
            job_location = job["workCity"]["name"]
            company_name = job["companyName"]
            job_url = f"https://www.1111.com.tw/job/{job_id}"
            job_detail = analaze_pages(job_url)

            data = {
                "job_title": job_title,
                "company_name": company_name,
                "location": job_location,
                "job_url": job_url,
                "job_description": job_detail["description"],
                "required_skills": job_detail["skills"],
                "salary": job_detail["salary"],
                "experience": job_detail["experience"],
                "work_type": job_detail["work_type"],
                "category": "軟體 / 工程類人員",
                "sub_category": category_name,
                "platform": "1111",
            }
            result.append(data)

        page += 1

    # save_to_csv(result, f"1111_jobs_{category_name}")

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
        request_url = f"{BASE_URL}?page={page}&jobPositions={category_id}"
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
