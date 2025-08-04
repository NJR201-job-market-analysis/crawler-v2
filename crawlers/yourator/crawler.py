import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote


BASE_URL = "https://www.yourator.co"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}

# 列出所有可能的工作經歷關鍵字
EXPERIENCE_KEYWORDS_SIMPLE = [
    "年以上",
    "年經驗",
    "年資歷",
    "年經歷",
    "年工作經驗",
    "工作經驗",
    "工作資歷",
    "年開發經驗",
    "開發資歷" "one year",
    "two years",
    "three years",
    "four years",
    "five years",
    "six years",
    "seven years",
    "eight years",
    "nine years",
    "ten years",
    "years of experience",
    "years experience",
    "at least",
    "minimum of",
    # ...可再擴充...
]

COMMON_SKILLS = [
    # 主流語言/框架
    "JavaScript",
    "Javascript",
    "Typescript",
    "TypeScript",
    "Node.js",
    "NodeJs",
    "Node",
    "Python",
    "Java",
    "Go",
    "Golang",
    "Flutter",
    "C#",
    "C++",
    "C",
    "PHP",
    "Ruby",
    "Swift",
    "Kotlin",
    "Scala",
    "Perl",
    "Rust",
    "Objective-C",
    ".NET",
    # 資料庫
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MSSQL",
    "Oracle",
    "MongoDB",
    "Redis",
    "ElasticSearch",
    "SQLite",
    # 前端
    "HTML5",
    "CSS3",
    "HTML",
    "CSS",
    "Sass",
    "Less",
    "React",
    "React Native",
    "React.js" "ReactJs",
    "Redux",
    "Nextjs",
    "NextJs",
    "Vue",
    "Vue.js",
    "Angular",
    # DevOps/雲端
    "Shell Script",
    "Bash",
    "Linux",
    "Unix",
    "AWS",
    "GCP",
    "Azure",
    "Google Cloud",
    "Amazon Web Services",
    "Microsoft Azure",
    "Docker",
    "Kubernetes",
    "K8s",
    "Git",
    "GitHub",
    "GitLab",
    "CI/CD",
    "Jenkins",
    "GitHub Actions",
    "GitLab CI",
    # API/通訊
    "GraphQL",
    "Graphql",
    "RESTful",
    "Restful",
    "gRPC",
    "Pubsub",
    "Message Queue",
    "RabbitMQ",
    "Kafka",
    "Nginx",
    "Apache",
    # 其他
    "Agile",
    "Scrum",
    "Kanban",
    # ...可再擴充...
]


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


def crawl_yourator_jobs_by_category(category):
    results = []
    page = 1
    while True:
        job_list_res = fetch_job_list(page, category)
        if not job_list_res or not job_list_res["payload"]["jobs"]:
            break

        for job in job_list_res["payload"]["jobs"]:
            job_url = BASE_URL + job["path"]
            print(f"Processing: {job_url}")
            html = fetch_job_html(job_url)
            experience = fetch_job_experience(html)
            if job["tags"]:
                skills = ",".join(job["tags"])
            else:
                skills = fetch_skills_from_detail(html)

            results.append(
                {
                    "job_title": job["name"],
                    "company_name": job["company"]["brand"],
                    # "work_type": job['type'],
                    "required_skills": skills,
                    # "job_description": job['description'],
                    # "location": job["location"],
                    # "salary": job["salary"],
                    "experience": experience,
                    "job_url": job_url,
                    "category": "軟體／工程類人員",
                    "sub_category": category,
                    "platform": "Yourator",
                }
            )
            time.sleep(1)
        if not job_list_res["payload"]["hasMore"]:
            break
        page += 1

    return results
