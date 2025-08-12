import re

from .constants import number_text_mapping


def extract_salary_range(salary_str):
    numbers = re.findall(r"\d{1,3}(?:,\d{3})*", salary_str)
    numbers = [int(num.replace(",", "")) for num in numbers]

    if len(numbers) == 1:
        return numbers[0], None
    elif len(numbers) >= 2:
        return numbers[0], numbers[1]
    else:
        return None, None


def extract_experience_min(experience_text):
    if not experience_text:
        return None

    if experience_text == "不拘":
        return 0

    # 1. 找阿拉伯數字
    match = re.search(r"\d+", experience_text)
    if match:
        return int(match.group())

    # 2. 找中文數字
    for ch, num in number_text_mapping.items():
        if ch in experience_text:
            return int(num)

    # 3. 都找不到
    return None
