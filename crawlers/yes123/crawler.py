import urllib.request as req
import bs4 as bs
import urllib.request as req
import urllib.parse
import pandas as pd
import json
import re
import csv
import sys

fn = 'common_skills.json'
with open(fn, 'r', encoding='utf-8') as f:
    # json.load() 會直接將 JSON 內容解析成 Python 物件
    # 因為 JSON 檔案的根元素是陣列，所以它會被解析為一個 Python 列表
    COMMON_SKILLS = json.load(f)

def get_url(keyword, mode = 1, page = 0):
    """
    根據關鍵字、關鍵字模式、頁數組合出網址。
    Args:
        keyword：職缺關鍵字。
        mode：關鍵字模式。
        page：頁數，組合網址用，每頁30筆，從0開始，因此第一頁為0、第二頁為30...以此類推。

        p.s.
        - mode 0 為搜尋關鍵字模式：比較模糊，精準度不如以下兩者，因此不建議採用
        - mode 1 為工作領域模式，參考網站提供的job_mode.json, job_mode2.json找出編碼，即可組合出網址。
        - mode 2 為職缺關鍵字模式，參考網站提供的work_modeNote.json，即可組合出網址。
        為節省時間，現在先不載入mode 1和mode 2所需資料表，先挑選我們需要的一些關鍵字。

    Returns:
        一個url字串。
    """

    job_mode_dict = {"網路／軟體":"3_1002_0001_0000"}
    work_mode_dict = {"軟體專案主管":"2_1011_0001_0001", 
                 "電子商務主管":"2_1011_0001_0002",
                 "網路程式設計師":"2_1011_0001_0003",
                 "系統規劃分析師":"2_1011_0001_0004",
                 "軟體工程師":"2_1011_0001_0005",
                 "演算法開發工程師":"2_1011_0001_0006",
                 "通訊軟體工程師":"2_1011_0001_0007",
                 "韌體工程師":"2_1011_0001_0008",
                 "BIOS工程師":"2_1011_0001_0009",
                 "電玩程式設計師":"2_1011_0001_0010",
                 "資訊助理人員":"2_1011_0001_0011",
                 "iOS工程師":"2_1011_0001_0012",
                 "Android工程師":"2_1011_0001_0013",
                 "全端工程師":"2_1011_0001_0014",
                 "前端工程師":"2_1011_0001_0015",
                 "後端工程師":"2_1011_0001_0016",
                 "資料工程師":"2_1011_0001_0017",
                 "數據分析師":"2_1011_0001_0018",
                 "資料科學家":"2_1011_0001_0019",
                 "其他資訊專業人員":"2_1011_0001_8001",
                 "MIS／網管主管":"2_1011_0002_0001",
                 "資料庫管理":"2_1011_0002_0002",
                 "MIS程式設計師":"2_1011_0002_0003",
                 "網路管理工程師":"2_1011_0002_0004",
                 "網路安全分析師":"2_1011_0002_0005",
                 "MES工程師":"2_1011_0002_0006",
                 "系統維護／操作人員":"2_1011_0002_0007",
                 "資訊設備管制人員":"2_1011_0002_0008",
                 "資安工程師":"2_1011_0002_0009",
                 }
    
    if mode == 0:   # 關鍵字模式
        # keyword = keyword.replace(' ',"%20")
        mode_text = "find_key2"
        url = f"https://www.yes123.com.tw/wk_index/joblist.asp?find_key2={keyword}&order_ascend=desc&search_key_word={keyword}"

        # 將中文部分進行編碼
        parsed = urllib.parse.urlsplit(url)
        encoded_path = urllib.parse.quote(parsed.path)
        encoded_query = urllib.parse.quote(parsed.query, safe="=&")
        # 組合回完整 URL
        url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, encoded_path, encoded_query, parsed.fragment))
        
    elif mode == 1:
        mode_text = "find_job_mode1"
        url = f"https://www.yes123.com.tw/wk_index/joblist.asp?{mode_text}={job_mode_dict[keyword]}&order_ascend=desc"
    elif mode == 2:
        mode_text = "find_work_mode1"
        url = f"https://www.yes123.com.tw/wk_index/joblist.asp?{mode_text}={work_mode_dict[keyword]}&order_ascend=desc"
    else:
        url = "https://www.yes123.com.tw/wk_index/joblist.asp?find_job_mode1=3_1002_0001_0000&order_ascend=desc"
    
    if page > 0:
        url += f"&strrec={30*page}&search_from=joblist"
    return url
    
def extract_english_words(text):
    """
    從中英夾雜的文字中，提取所有英文單字，組成列表後回傳。
    """
    # 定義一個正規表達式模式來匹配英文單字
    # \b 是一個單字邊界 (word boundary)，確保匹配的是完整的單字
    # [a-zA-Z]+ 匹配一個或多個英文字母
    pattern = r'\b[a-zA-Z]+\b'
    
    # 使用 re.findall 找出所有符合模式的字串
    english_words = re.findall(pattern, text)
    english_words = [word.lower() for word in english_words]
    
    return english_words


def get_html_from_url(url):
    """
    以美麗湯解析傳入網址，並回傳html。
    """
    r = req.Request(url)
    r.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    resp = req.urlopen(r)
    html = bs.BeautifulSoup(resp, features="html.parser")
    return html

def _extract_skills(html):
    """
    根據傳入html，找出有在技能清單內的技能，回傳以逗點為間隔組合好的字串。
    """
    # 找出「技能與求職專長」的h3，下面的ul裡面，就是所有技能的文字。
    try:
        h3_skills = html.find('h3', string='技能與求職專長')
        ul_skills = h3_skills.find_next_sibling('ul')
    except Exception as e:
        return ""

    all_text = ul_skills.get_text(strip=True)

    # 因為技能都是英文單字，先將文字內所有英文單字提取出來
    skills_list = extract_english_words(all_text)

    # 然後與技能清單逐一比對，有的話就加入一個set
    found_skills = set()
    for skill in COMMON_SKILLS:
        if skill.lower() in skills_list:
            found_skills.add(skill)
    if not found_skills:
        return ""
    return ",".join(sorted(found_skills)) if found_skills else ""   

def crawl_a_job(job_link):
    """
    傳入單一筆職缺的網址，爬取所需資訊，回傳該筆職缺的字典。
    """
    html = get_html_from_url(job_link)
    descriptions = html.find_all('div', {'class': 'job_explain'})

    li_items = []
    for description in descriptions:
        ul_item = description.find('ul')
        li_items += ul_item.find_all('li')

    # 我們需要的項目（還沒爬更新日期）
    map_dict = {
        '工作內容': 'job_description',
        '工作性質': 'work_type',
        '上班時段': 'work_time',
        '工作地點': 'address',
        '學歷要求': 'degree',
        '科系要求': 'department',
        '工作經驗': 'experience',
        '外語能力': 'qualification_bonus',
        '連絡人': 'contact_person'
    }

    job_dict = {}

    # 初始化空值
    for key, value in map_dict.items():
        job_dict[value] = ''

    for li_item in li_items:
        # 先爬取這個項目的副標題
        left_title = li_item.find('span', {'class': 'left_title'})
        if left_title is None:
            continue
        left_title_text = left_title.get_text()
        # 再一一核對職缺說明有沒有這一項
        for key, value in map_dict.items():
            if key in left_title_text:
                right_main_text = li_item.find('span', {'class': 'right_main'}).get_text()
                job_dict[value] = right_main_text.strip()

    # 技能專長獨立爬取
    job_dict["required_skills"] = _extract_skills(html)

    return job_dict

def crawl_a_page(html):
    """
    傳入職缺列表網址（只有一頁），爬取所需資訊，回傳最多30筆職缺的字典列表。
    """
    job_items = html.find_all("div",{"class":"Job_opening_M"})
    job_list = []

    i = 1
    for job_item in job_items:
        divs = job_item.find("div",{"class":"Job_opening_item_info_M"}).find_all('div')
        # 工作名稱
        title_text = divs[1].find('h5').get_text().strip()
        # 以下兩個之後會在table「company」獨立建表
        company_text = divs[2].find('h5').get_text().strip()
        # 地區
        location_text = divs[3].find('h5').get_text().strip()
        salary_text = divs[4].find('h5').get_text().strip()

        # tags: 有些有有些沒有
        tags = ''
        if len(divs) > 5:
            for div in divs[5:]:
                tags += div.get_text().strip()

        job_dict = {
            "job_title": title_text,
            "salary": salary_text,
            "company_name": company_text,
            "location": location_text,
            "tags": tags
        }
        
        # cmd動態進度條，每爬完一個職缺就會加一
        sys.stdout.write(f"\rProgress: Job {i} / {len(job_items)}    ") # Add some spaces to overwrite longer previous numbers
        sys.stdout.flush() # Forces the output to be displayed immediately

        # 準備爬取該筆職缺連結
        job_link = job_item.find('a')['href']
        job_link = 'https://www.yes123.com.tw/wk_index/' + job_link
        page_dict = crawl_a_job(job_link)

        # 結合主頁面和單一工作頁面所得資訊，加入串列中
        job_dict = job_dict | page_dict
        job_list.append(job_dict)

        # 準備爬下一筆職缺
        i += 1
        
    sys.stdout.write("\n") # Print a newline character at the end to move to the next line
    return job_list

def crawl_all_pages(html, keyword, mode):
    """
    傳入第一頁的html、搜尋關鍵字與模式，爬取所有頁面的職缺後，回傳完整的職缺字典列表。
    """
    # 從頁面button找出有幾頁
    page_btn = html.find(id='inputState')
    if not page_btn:
        pages = 1
    else:
        pages = len(page_btn.find_all('option'))
    print('Total:',pages,'pages')

    # 開始一頁一頁爬蟲
    page = 0
    job_list = []
    while page < pages:
        print('------------------------------------------')
        print('Ready to crawl page',page+1,'/',pages,'...')
        job_list += crawl_a_page(html)
        page += 1
        url = get_url(keyword, mode, page)
        html = get_html_from_url(url)
    return job_list

def data_to_json(data, json_filepath):
    """
    傳入職缺字典列表，存成.json檔案
    """
    with open(json_filepath, 'w', encoding='utf-8') as f:
        # endure-ascii 會把所有東西轉成英文
        json.dump(job_list, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved to '{json_filepath}'")

def data_to_csv(data, csv_filepath):
    """
    傳入職缺字典列表，存成.csv檔案
    """
    fieldnames = data[0].keys() # Assumes all dictionaries have the same keys

    with open(csv_filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Successfully saved to '{csv_filepath}'")
    return

if __name__ == '__main__':
    # mode 0 為搜尋關鍵字模式
    # keyword, mode = '軟體 工程師', 0

    # mode 1 為工作領域模式
    keyword, mode = "網路／軟體", 1

    # mode 2 為職缺關鍵字模式
    # keyword, mode = '資料工程師', 2

    url = get_url(keyword, mode)
    print('Start page:',url)
    html = get_html_from_url(url)
    job_list = crawl_all_pages(html, keyword, mode)

    # 存成 .json 和 .csv
    if ' ' in keyword:
        keyword = keyword.replace(' ','+')
    fn = "yes123_" + keyword
    data_to_json(job_list, fn + '.json')
    data_to_csv(job_list, fn + '.csv')