COMMON_SKILLS = [
    # 主流語言/框架
    "JavaScript",
    "Typescript",
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

job_category_mapping = {
    "iOS工程師": "APP工程師",
    "Android工程師": "APP工程師",
    "前端工程師": "前端工程師",
    "後端工程師": "後端工程師",
    "全端工程師": "全端工程師",
    "數據分析師／資料分析師": "數據分析師",
    "軟體工程師": "軟體工程師",
    "軟體助理工程師": "軟體工程師",
    "軟體專案主管": "專案/技術主管",
    "系統分析師": "系統分析師",
    "資料科學家": "資料科學家",
    "資料工程師": "資料工程師",
    "AI工程師": "AI工程師",
    "演算法工程師": "演算法工程師",
    "電玩程式設計師": "電玩程式設計師",
    "Internet程式設計師": "網站開發人員",
    "區塊鏈工程師": "區塊鏈工程師",
    "通訊軟體工程師": "軟體工程師",
    "電子商務技術主管": "專案/技術主管",
    "商業分析師": "商業分析師",
    "其他資訊專業人員": "其他資訊專業人員",
    "DevOps 工程師": "DevOps工程師",
    "機器學習工程師": "機器學習工程師",
    "系統工程師": "系統工程師",
    "網路管理工程師": "網路管理工程師",
    "雲端工程師": "雲端工程師",
    "網路安全分析師": "網路安全分析師",
    "MES工程師": "MES工程師",
    "MIS程式設計師": "MIS工程師",
    "資料庫管理人員": "資料庫管理人員",
    "MIS／網管主管": "專案/技術主管",
    "區塊鏈軟體工程師": "區塊鏈工程師",  # Cake
    "QA 測試工程師": "軟體測試工程師",  # Cake
    "DevOps 系統管理員": "DevOps工程師",  # Cake
    "數據工程師": "資料工程師",  # Cake
    "Python 開發人員": "軟體工程師",  # Cake
    "iOS 開發人員": "APP工程師",  # Cake
    "Java 開發人員": "軟體工程師",  # Cake
    "研發": "研發工程師",  # Cake
    "網站開發人員": "網站開發人員",  # Cake
    "Android 開發人員": "APP工程師",  # Cake
    "PHP 開發人員": "軟體工程師",  # Cake
    "Ruby on Rails 開發人員": "軟體工程師",  # Cake
    "系統架構": "系統工程師",  # Cake
    "C/C++ 開發人員": "軟體工程師",  # Cake
    "大數據工程師": "資料工程師",  # Cake
    "Node.js 開發人員": "軟體工程師",  # Cake
    "開發經理": "專案/技術主管",  # Cake
    "資料庫管理員": "資料庫管理人員",  # Cake
    "技術長": "專案/技術主管",  # Cake
    "跨平台應用程式開發人員": "APP工程師",  # Cake
    ".NET 開發人員": "軟體工程師",  # Cake
    "技術經理": "專案/技術主管",  # Cake
    "軟／韌體測試人員": "軟體測試工程師",  # 1111
    "CIM工程師": "其他資訊專業人員",  # 1111
    "網站技術主管": "專案/技術主管",  # 1111
    "網站程式設計師": "網站開發人員",  # 1111
    "電子商務技術主管": "專案/技術主管",  # 1111
    "資料科學工程主管": "專案/技術主管",  # 1111
    "數據科學家": "資料科學家",  # 1111
    "數據分析師": "數據分析師",  # 1111
    "數據管理師": "資料工程師",  # 1111
    "數據架構師": "資料工程師",  # 1111
    "演算法開發工程師": "演算法工程師",  # 1111
    "資料科學助理工程師": "資料科學家",  # 1111
    "雲服務/雲計算工程主管": "專案/技術主管",  # 1111
    "雲端系統管理員": "雲端工程師",  # 1111
    "雲端架構師": "雲端工程師",  # 1111
    "雲端應用工程師": "雲端工程師",  # 1111
    "雲端網路工程師": "雲端工程師",  # 1111
    "雲端自動化工程師": "雲端工程師",  # 1111
    "雲服務/雲計算助理工程師": "雲端工程師",  # 1111
    "系統主管": "專案/技術主管",  # 1111
    "自動化測試工程師": "軟體測試工程師",  # 1111
    "電玩工程師": "電玩程式設計師",  # 1111
    "APP工程師": "APP工程師",  # 1111
}
