import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

BASE_URL = 'https://www.yourator.co'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}

# 列出所有可能的工作經歷關鍵字
EXPERIENCE_KEYWORDS_SIMPLE = [
    "年以上", "年經驗", "年資歷", "年經歷", "年工作經驗", "工作經驗", "工作資歷", "年開發經驗", "開發資歷"
    "one year", "two years", "three years", "four years", "five years",
    "six years", "seven years", "eight years", "nine years", "ten years",
    "years of experience", "years experience", "at least", "minimum of"
    # ...可再擴充...
]

COMMON_SKILLS = [
    # 主流語言/框架
    "JavaScript", "Javascript", "Typescript", "TypeScript", "Node.js", "NodeJs", "Node", "Python", "Java", "Go", "Golang", "Flutter",
    "C#", "C++", "C", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "Perl", "Rust", "Objective-C", ".NET",
    # 資料庫
    "SQL", "MySQL", "PostgreSQL", "MSSQL", "Oracle", "MongoDB", "Redis", "ElasticSearch", "SQLite",
    # 前端
    "HTML5", "CSS3", "HTML", "CSS", "Sass", "Less", "React", "React Native", "React.js" "ReactJs", "Redux", "Nextjs", "NextJs", "Vue", "Vue.js", "Angular",
    # DevOps/雲端
    "Shell Script", "Bash", "Linux", "Unix",
    "AWS", "GCP", "Azure", "Google Cloud", "Amazon Web Services", "Microsoft Azure",
    "Docker", "Kubernetes", "K8s", "Git", "GitHub", "GitLab", "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI",
    # API/通訊
    "GraphQL", "Graphql", "RESTful", "Restful", "gRPC", "Pubsub", "Message Queue", "RabbitMQ", "Kafka", "Nginx", "Apache",
    # 其他
    "Agile", "Scrum", "Kanban",
    # ...可再擴充...
]

# 取得職缺列表
def fetch_job_list(page):
    url = (
        f"{BASE_URL}/api/v4/jobs?category[]=%E5%89%8D%E7%AB%AF%E5%B7%A5%E7%A8%8B&category[]=%E5%BE%8C%E7%AB%AF%E5%B7%A5%E7%A8%8B&category[]=%E5%85%A8%E7%AB%AF%E5%B7%A5%E7%A8%8B&category[]=%E6%B8%AC%E8%A9%A6%E5%B7%A5%E7%A8%8B&category[]=%E8%B3%87%E6%96%99%E5%BA%AB&category[]=DevOps%20%2F%20SRE&category[]=%E8%BB%9F%E9%AB%94%E5%B7%A5%E7%A8%8B%E5%B8%AB&category[]=%E9%9B%B2%E7%AB%AF%E5%B7%A5%E7%A8%8B%E5%B8%AB&category[]=%E7%B3%BB%E7%B5%B1%E6%9E%B6%E6%A7%8B%E5%B8%AB&category[]=%E6%95%B8%E6%93%9A%20%2F%20%E8%B3%87%E6%96%99%E5%88%86%E6%9E%90%E5%B8%AB&negotiable=false&page={page}&sort=recent_updated&task_based=false"
    )
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
def fetch_job_experience(html):
    try:
        soup = BeautifulSoup(html, "html.parser")

        texts = soup.stripped_strings
        for line in texts:
            for keyword in EXPERIENCE_KEYWORDS_SIMPLE:
                if keyword in line:
                    return line
        return "不限"
    except Exception as e:
        print(f"Failed to fetch job detail: {e}")
        return ""

# 取得職缺詳細資訊的技能
def fetch_skills_from_detail(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        found_skills = set()
        for line in soup.stripped_strings:
            line_lower = line.lower()
            for skill in COMMON_SKILLS:
                if skill.lower() in line_lower:
                    found_skills.add(skill)
        return ",".join(sorted(found_skills)) if found_skills else ""
    except Exception as e:
        print(f"Failed to parse skills: {e}")
        return ""

def crawler(filename):
    results = []
    page = 1
    while True:
        job_list_res = fetch_job_list(page)
        if not job_list_res or not job_list_res['payload']['jobs']:
            break

        for job in job_list_res['payload']['jobs']:
            job_url = BASE_URL + job['path']
            print(f"Processing: {job_url}")
            html = fetch_job_html(job_url)
            experience = fetch_job_experience(html)
            if job['tags']:
                skills = ",".join(job['tags'])
            else:
                skills = fetch_skills_from_detail(html)

            results.append({
                "職缺": job['name'],
                "公司": job['company']['brand'],
                "要求技能": skills,
                "公司簡述": "",
                "地點": job['location'],
                "薪資": job['salary'],
                "經驗": experience,
            })
            time.sleep(1)
        if not job_list_res['payload']['hasMore']:
            break
        page += 1

    df = pd.json_normalize(results)
    df.to_csv(filename + ".csv", encoding="utf-8")