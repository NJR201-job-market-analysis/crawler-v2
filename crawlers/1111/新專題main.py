import urllib.request as req
import bs4 as bs
import pandas as pd
import urllib
import json
import ssl
import os
# 直接爬會跳出ssl認證沒過, ssl這行是google來的指令 貼上去後才可以爬取
ssl._create_default_https_context = ssl._create_unverified_context
url=""
def analaze_pages(url):
    r=req.Request(url, headers={
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    })
    resp=req.urlopen(r)
    content=resp.read().decode("utf-8")
    html=bs.BeautifulSoup(content, "html.parser")
    c_name=html.find("h2",{"class":"inline font-normal text-base text-[#212529]"}).text
    job_titles=html.find("h1",{"class":"text-gray-800"}).text
    job_todo=html.find("div",{"class":"whitespace-pre-line"}).text
    skills=html.find_all("p",{"class":"underline-offset-1"})
    #電腦專長(前面是電腦專長list, list最後一項卻是抓出公司名稱, 所以pop掉.
    #但如果廣告沒有刊登電腦專長, 一樣會抓到公司名稱, 所以沿用pop後變成的空集合, 賦值"沒有刊登電腦專長"
    skill_list=[]
    for skill in skills:
        skill_list.append(skill.text)
    skill_list.pop()
    if skill_list==[]:
        skill_list="沒有刊登電腦專長"
    #地址的標頭和"class"有兩種...#爬出來的地址會參雜一堆空格和換行, 這裡先設一個空list,
    #再用for in回圈寫入有意義的文字(空格和換行符號不寫入)
    work_place=html.find("p",{"class":"mb-4"}) #第一種路徑
    if work_place==None: #如果第一種路徑抓不到
        work_place=html.find("div",{"class":"md:items-center content"}).p.text #就它了
        work_place_location=""
        for w in work_place:
            if w==" " or w=="\n":
                continue
        else:
            work_place_location=work_place_location+w
    else:
        work_place_location=""
        for s in work_place.text:
            if s==" " or s=="\n":
                continue   #不寫入空格" "和換行符號"\n" 遇到就回前面, 不執行append(a)
            work_place_location=work_place_location+s

    #遠端 有的公司直接缺少該欄位 用class會撈到別的東西 所以查找關鍵字"遠端上班"的"遠"
    # (不用"端"是因為會撈出前端後端)(應該有更好的解法, 待我再研究XD)
    work_type=html.find_all("div",{"class","content"})
    keywords={"遠",}
    work_type_=set()
    for w in work_type:
        if w.h3!=None:
            for keyword in w.h3.text:
                if keyword in keywords:
                    work_type_.add(w.h3.text)
        if w.p!=None:
            for keyword in w.p.text:
                if keyword in keywords:
                    work_type_.add(w.p.text)
    if work_type_==set():  #QQ共用的太多了, 一直重複查找, 先用set()刪掉重複抓到的
        work_type_="沒有遠距"
    else:
        work_type_=",".join(work_type_)
        if work_type_=="發展遠景":
            work_type_="沒有遠距"
    #工作經驗
    job_exs=html.find_all("div",{"class":"content"})
    for job_ex in job_exs:
        if job_ex.h3!=None:
            if job_ex.h3.text=="工作經驗":
                job_exs=job_ex.p.text
    #出差
    job_trips=html.find_all("div",{"class":"content"})
    for job_trip in job_trips:
        if job_trip.h3!= None:
            if job_trip.h3=="其他說明":
                job_trips=job_trip.p.text
            else:
                job_trips="不用出差"
    #更新時間
    updata_time=html.find("span",{"class":"leading-[1.8] text-[16px]"}).text    

    data = {
        "職稱":job_titles,
        "公司名稱":c_name,
        "工作內容(職缺描述)":job_todo,
        "電腦專長":skill_list,
        "工作地點":work_place_location,
        "工作經驗":job_exs,
        "遠距工作":work_type_,
        "其他說明":job_trips,
        "更新日期":updata_time,
        }
    return data

 #查找的關鍵字 中間用+連接 ex.software+engineer
looking_for=urllib.parse.quote("軟體+工程師")
looking_for="desc&ks="+urllib.parse.quote("軟體+工程師") #中文關鍵字
p_start=1   #從第幾頁開始找
p_limit=2   #找到第幾頁
wfh=False      #預設不設條件. 但只想找遠端工作, 改成True
ex=False       #預設不設條件. 但要找工作經驗"不拘"的, 改成False
w_place=[]  #預設不限, 若要特定的縣市, 輸入"兩個字", 並以逗號相隔 ex.["台北","桃園"]
table=[]       #這是張無關緊要的桌子

def find_all_pages(looking_for,p_start,p_limit,w_place,wfh,ex):
    for i in range(p_start,p_limit+1):
        url=f"https://www.1111.com.tw/search/job?page={i}&col=ab&sort=desc&ks={looking_for}"
        r=req.Request(url, headers={
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        })
        resp=req.urlopen(r)
        content=resp.read().decode("utf-8")
        html=bs.BeautifulSoup(content, "html.parser")
        job_list=html.find_all("div",{"class":"shrink-0"})
        for h in job_list:
            if h.find("a",{"class":"mb-1"})!=None:
                job_url="https://www.1111.com.tw"+h.find("a",{"class":"mb-1"})["href"]
                # print(job_url)
                # print("-"*10)
                data = analaze_pages(job_url)
                if wfh==True and data["遠距工作"]=="沒有遠距":
                    continue   
                if ex==True and data["工作經驗"]!="不拘":
                    continue
                if w_place!=[] and data["工作地點"][0:2] not in w_place:
                    continue
                table.append(data)
    return table

#方便日後擴充使用, 現在暫時只有生成資料夾和路徑的功能
class File:
    def __init__(self,name):
        self.name=name
        self.file=None #尚未開啟檔案: 初期是None
        self.path_name=None
    def path(self,path_name):
        if not os.path.exists(path_name): #如果資料夾不存在就創起來
            os.makedirs(path_name)
        self.path_name=path_name+"/"+self.name #資料夾加上檔名(形成路徑)
