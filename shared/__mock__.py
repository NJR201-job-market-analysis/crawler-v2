jobs_to_insert = [
    {
        "job_title": "資深後端工程師 (Python)",
        "company_name": "未來科技公司",
        "job_url": "https://example.com/job/12345",  # 唯一的網址，用來判斷是新增還是更新
        "salary_min": 50000,
        "salary_max": 80000,
        "salary_type": "月薪",
        # ... 其他 jobs 表的欄位 ...
        # 關鍵：將分類和技能以列表形式提供
        "categories": ["软体/技术主管", "後端工程師"],
        "skills": ["Python", "Django", "PostgreSQL", "Docker"],
    },
    # ... 可以有多筆職缺 ...
]
