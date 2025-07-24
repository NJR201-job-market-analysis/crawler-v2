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
    #公司名稱
    c_name=html.find("h2",{"class":"inline font-normal text-base text-[#212529]"}).text
    #聯絡人
    contact_info=html.find("div",{"class":"mb-8 grid gap-4"}).p.text
    #職缺名稱
    job_titles=html.find("h1",{"class":"text-gray-800"}).text
    #工作內容說明
    job_todo=html.find("div",{"class":"whitespace-pre-line"}).text
    #薪資
    job_salary=html.find("div",{"class":"text-main"}).text.strip("查看薪資水平")
    #上班時段
    if html.find("li",{"class":"flex justify-start items-center"}).p!=None:
        work_time=html.find("li",{"class":"flex justify-start items-center"}).p.text
    else:
        work_time="未標示"
    #工作性質
    work_type=html.find("li",{"class":"flex flex-wrap"}).text
    #福利
    #加分技能 外語 
    qualification_bonus1=html.find("li",{"class":"block"})
    if qualification_bonus1!=None:
        qualification_bonus1=qualification_bonus1.text.split("｜")
        qualification_bonus1=":".join(qualification_bonus1).replace("、 ","、")
    else:
        qualification_bonus1="外語能力不拘"
    #加分技能 駕照
    qualification_bonus=html.find_all("div",{"class","flex justify-start items-center"})
    if qualification_bonus[1].p!=None:
        qualification_bonus=qualification_bonus[1].p.text
        if "車" in qualification_bonus:
            qualification_bonus="駕照: "+qualification_bonus
        else:
            qualification_bonus="無須具備駕照"
    else:
        qualification_bonus="無須具備駕照"
    #科系/學類
    if html.find("a",{"class":"flex justify-start items-center"})!=None:
        htmlsmall=html.find_all("a",{"class":"flex justify-start items-center"})
        department=[]
        for hl in htmlsmall:
            if "學" in hl.p.text:
                department.append(hl.p.text)
        department=", ".join(department)
        if department=="":
            department="不拘"
    else:
        department="不拘"
    # 學歷要求
    if html.find("div",{"class":"grid gap-4"})!=None:
        htmlsmall=html.find("div",{"class":"grid gap-4"}).find_all("div",{"class":"content"})
        for hl in htmlsmall:
            if hl.h3!=None:
                if hl.h3.text=="學歷要求":
                    degree=hl.p.text
    else:
        degree="不拘"
    #休假制度
    leave_policy=html.find("li",{"class","flex after-comma-not-last"})
    if leave_policy!=None:
        leave_policy=leave_policy.find("div",{"class":"flex justify-start items-center"}).text
    else:
        leave_policy="未標示休假制度"

     #電腦專長
    skills=html.find_all("p",{"class":"underline-offset-1"})
    #電腦專長(前面是電腦專長list, list最後一項卻是抓出公司名稱, 所以pop掉.
    #但如果廣告沒有刊登電腦專長, 一樣會抓到公司名稱, 所以沿用pop後變成的空集合, 賦值"沒有刊登電腦專長"
    skill_list=[]
    for skill in skills:
        skill_list.append(skill.text)
    skill_list.pop()
    if skill_list==[]:
        skill_list="沒有刊登電腦專長"
    else:
        if "公司" in skill_list[-1]:
            skill_list.pop()
    #地址的標頭和"class"有兩種...#爬出來的地址會參雜一堆空格和換行,(空格和換行符號不寫入)
    work_place=html.find("p",{"class":"mb-4"}) #第一種路徑
    if work_place==None: #如果第一種路徑抓不到
        work_place=html.find("div",{"class":"md:items-center content"}).p.text #就它了
        aa=work_place.split()
        work_place_location=" ".join(aa)
    else:
        bb=work_place.text.split()
        work_place_location=" ".join(bb)

    #工作經驗
    job_exs=html.find_all("div",{"class":"content"})
    for job_ex in job_exs:
        if job_ex.h3!=None:
            if job_ex.h3.text=="工作經驗":
                job_exs=job_ex.p.text
    #工作地點
    work_place_city=work_place_location.split()[0]
    #更新時間
    updata_time=html.find("span",{"class":"leading-[1.8] text-[16px]"}).text    

    data = {
        "公司名稱":c_name,
        "地址":work_place_location,
        "聯絡人":contact_info,
        "職缺名稱":job_titles,
        "工作內容說明":job_todo,
        "薪資上下限":job_salary,
        "上班時段":work_time,
        "工作性質":work_type,
        "工作地點":work_place_city,
        "工作地址":work_place_location,
        "加分技能":qualification_bonus+"/  "+qualification_bonus1,
        "工作經驗":job_exs,
        "程式語言":skill_list,
        "科系/學類":department,
        "學歷要求":degree,
        "休假制度":leave_policy,
        "職缺更新日期":updata_time,
        }
    return data

 #查找的關鍵字 中間用+連接 ex.software+engineer
looking_for=urllib.parse.quote("軟體+工程師")
looking_for="desc&ks="+urllib.parse.quote("軟體+工程師") #中文關鍵字
p_start=1   #從第幾頁開始找
p_limit=2   #找到第幾頁

table=[]       #這是張無關緊要的桌子

def find_all_pages(looking_for,p_start,p_limit):
    for i in range(p_start,p_limit+5):
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
                table.append(data)
    return table



