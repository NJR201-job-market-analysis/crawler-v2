import 新專案1111main1 as main

#(一)查找資料條件, 我們希望獲得以下資訊(職缺): 
#Table company:
#"公司名稱", "地址","聯絡人"
# Table job:
# "職缺名稱", "工作內容(職缺描述)", 
#"工作內容說明", "薪資上下限","上班時段","工作性質","工作地點",
#"加分技能(外語, 駕照)" ,"工作經驗", "程式語言","科系/學類","學歷要求",
# "休假制度" , "職缺更新日期"

#(二)預設篩選條件, 請依需求自行修改
looking_for="desc&ks="+main.urllib.parse.quote("軟體+工程師") #查找中文關鍵字, 中間用+連接
#looking_for="software+python"         #查找英文關鍵字, 中間用+連接 ex."software+engineer"
p_start=1      #從第幾頁開始找
p_limit=10      #找到第幾頁

#(三)查找資料入口
main.find_all_pages(looking_for,p_start,p_limit)
df =main.pd.json_normalize(main.table)
# print("找到幾個職缺: ",df.shape[0]) #回傳找到幾個職缺

#(四)一步一步創資料夾存檔案
dn="肥貓大資料夾"    #創資料夾名稱
fn="jobtest61601"       #創檔名
if not main.os.path.exists(dn):
    main.os.makedirs(dn)
fn=dn+"/"+fn+".csv"
df.to_csv(fn, encoding="utf-8")