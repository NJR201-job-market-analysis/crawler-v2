from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# LinkedIn 帳號密碼
LINKEDIN_EMAIL = "LINKED_ACCOUNT"
LINKEDIN_PASSWORD = "LINKED_PASSWORD"

EXPERIENCE_KEYWORDS_SIMPLE = [
    "年以上",
    "年經驗",
    "年資歷",
    "年經歷",
    "年工作經驗",
    "年開發經驗",
    "開發資歷" "工作經驗",
    "工作資歷",
    "one year",
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
    "years of software",
    # ...可再擴充...
]

COMMON_SKILLS = [
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

    "SQL",
    "MySQL",
    "PostgreSQL",
    "MSSQL",
    "Oracle",
    "MongoDB",
    "Redis",
    "ElasticSearch",
    "SQLite",

    "HTML5",
    "CSS3",
    "HTML",
    "CSS",
    "Sass",
    "Less",
    "React",
    "ReactJs",
    "Redux",
    "Nextjs",
    "NextJs",
    "Vue",
    "Vue.js",
    "Angular",
    "Tailwind",

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

    "Agile",
    "Scrum",
    "Kanban",

]

def extract_skills(job_desc):
    try:
        found_skills = set()
        for line in job_desc.stripped_strings:
            line_lower = line.lower()
            for skill in COMMON_SKILLS:
                if skill.lower() in line_lower:
                    found_skills.add(skill)
        return ",".join(sorted(found_skills)) if found_skills else ""
    except Exception as e:
        print(f"Failed to parse skills: {e}")
        return ""


def extract_experience(job_desc):
    try:
        texts = job_desc.stripped_strings
        for line in texts:
            for keyword in EXPERIENCE_KEYWORDS_SIMPLE:
                if keyword in line:
                    return line
        return "不限"
    except Exception as e:
        print(f"Failed to fetch job detail: {e}")
        return ""


def crawler(filename, job_keyword, location):
    options = Options()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get("https://www.linkedin.com/login")

    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(3)

    base_url = "https://www.linkedin.com/jobs/search"
    query_params = {}
    if job_keyword:
        query_params["keywords"] = job_keyword
    if location:
        query_params["location"] = location
    query_string = urlencode(query_params)
    search_url = f"{base_url}/?{query_string}" if query_string else base_url
    print(search_url)
    driver.get(search_url)
    # 延遲頁面載入
    time.sleep(3)

    results = []

    page = 1
    while True:
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")

        print(
            f"目前在第 {page} 頁，URL: {driver.current_url}，找到 {len(job_cards)} 個職缺"
        )

        for card in job_cards:
            try:
                card.click()
                time.sleep(random.uniform(4, 8))
                soup = BeautifulSoup(driver.page_source, "html.parser")
                title = soup.select_one("h1 > a").get_text(strip=True)
                company = soup.select_one(
                    "div.job-details-jobs-unified-top-card__company-name > a"
                ).get_text(strip=True)
                location = soup.select_one(
                    "div.job-details-jobs-unified-top-card__tertiary-description-container > span > span:nth-child(1)"
                ).get_text(strip=True)
                job_desc = soup.select_one("div#job-details")
                skills = extract_skills(job_desc)
                experience = extract_experience(job_desc)

                results.append(
                    {
                        "職稱": title,
                        "公司": company,
                        "技能": skills,
                        "地點": location,
                        # linkedin 幾乎都沒有薪資
                        "薪資": "",
                        "經驗": experience,
                    }
                )
            except Exception as e:
                print("Error:", e)
                continue


        try:
            next_btn = driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='View next page']"
            )
            if next_btn.is_enabled():
                page += 1
                next_btn.click()
                time.sleep(random.uniform(4, 8))  # 等待新頁面載入
            else:
                break
        except Exception:
            break

    driver.quit()
    df = pd.json_normalize(results)
    df.to_csv(filename + ".csv", encoding="utf-8")

