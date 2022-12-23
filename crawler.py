# Import Modules
import re # Regular Expression (Regex)
from decimal import Decimal
from time import sleep
import requests
from bs4 import BeautifulSoup
import sqlite3 as sl

# Import My Modules
from lib.my_modules import gaussian_sleep as g_sleep
from lib.my_modules import print_progress as print_prog
from lib.my_modules import persistent_get as p_get

# gaussian_sleep用パラメータ: https://keisan.casio.com/exec/system/1180573188
mu = 10 # 待機時間の平均
sigma = 2 # 待機時間の標準偏差

# ユーザパラメータ
max_retries = 5 # request.get()失敗時の再試行回数

base_url = "https://rank.greeco-channel.com/access/?pg="

# SQLite3
db_name = "car.db"
con = sl.connect(db_name)
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS car(
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        mfr         TEXT NOT NULL,
        name        TEXT NOT NULL,
        type        TEXT,
        mdl         TEXT,
        gen         TEXT,
        grade       TEXT,
        mfr_year    TEXT,
        mdl_year    INTEGER,
        price       INTEGER,
        fuel        TEXT,
        kmpl        REAL,
        tax         INTEGER,
        w_tax       INTEGER,
        mand_ins    INTEGER,
        oil_chg     INTEGER,
        tire_chg    INTEGER,
        opt_ins     INTEGER,
        preloan_cst INTEGER,
        pstloan_cst INTEGER,
        insp_cst    INTEGER,
        doors       INTEGER,
        psngrs      INTEGER,
        ext_l       INTEGER,
        ext_w       INTEGER,
        ext_h       INTEGER,
        int_l       INTEGER,
        int_w       INTEGER,
        int_h       INTEGER,
        w_base      INTEGER,
        w_track_f   INTEGER,
        w_track_r   INTEGER,
        grnd_clr    INTEGER,
        turn_rad    REAL,
        weight      INTEGER,
        drive       TEXT,
        gears       INTEGER,
        trans       TEXT,
        eng_mdl     TEXT,
        eng_layout  TEXT,
        cc          TEXT,
        comp_ratio  REAL,
        comp_type   TEXT,
        kw          INTEGER,
        kw_rpm      INTEGER,
        trq_nm      INTEGER,
        trq_rpm     INTEGER,
        w_w_f       INTEGER,
        w_ratio_f   INTEGER,
        w_cnst_f    TEXT,
        w_rim_f     INTEGER,
        w_w_r       INTEGER,
        w_ratio_r   INTEGER,
        w_cnst_r    TEXT,
        w_rim_r     INTEGER,
        brake_f     TEXT,
        brake_r     TEXT,
        car_link    TEXT,
        img_link    TEXT,
        UNIQUE(mfr, name, type, mdl, gen, grade, mdl_year, mfr_year, price, car_link)
    );
""")
con.commit()

# Requests関連
session = requests.Session() # Sessionを使う事でrequestsに継続性が保たれる(例: Cookie)
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
}
session.headers.update(headers)

# 最初のページにアクセス
res = p_get(session, base_url, max_retries) # request.get(url)的な事をする
print(f"{'':#<90}")
print(f"{'':#<90}")
print(f"{'':#<90}")
print(res.status_code) # ステータスコードを表示する
c = res.content # 変数名: c = content
soup = BeautifulSoup(c, 'html.parser') # Soupを作る

# 最初のページからこれから取得するデータの概要を取得する
s = soup.find("div", class_="theContentWrap-ccc").find_all("p")[4].text # tag内のtextを取り出す
total_cars = int(re.search(r"全(.*?)件", s).group(1)) # Regexを使ってDBに登録されている車の総数を取り出す
total_pages= int(re.search(r"・(.*?)ページ中", s).group(1)) # Regexを使って総ページ数を取り出す
print("Total Cars: {}, Total Pages: {}".format(total_cars, total_pages))
print(f"{'':=<70}")

for page in list(range(181, total_pages+1)): # !!!LIMITER
    ######################################################
    # START: 車十件ずつの一覧ページ
    ######################################################
    # HTTP Request and create Soup
    url = base_url+str(page)
    c = p_get(session, url, max_retries).content
    soup = BeautifulSoup(c, 'html.parser')

    # Find all urls for each car
    urls = soup.find("table",class_="rank_tbl").find_all("a")[::2] # [::2]で２ステップにしている(謎の重複しているaタグがあるから)
    urls = [url["href"] for url in urls]    

    for car_url in urls: # !!!LIMITER
        c = p_get(session, car_url, max_retries).content
        soup = BeautifulSoup(c, 'html.parser')
        print(car_url)
        ######################################################
        # START: 車一件の詳細ページ
        ######################################################
        # Create an emtpy dict
        cols = ["mfr", "name", "type", # Common Identifier
                "mdl", "gen", "grade", # Additional Identifier
                "mfr_year", "mdl_year", # Years
                "price", "kmpl", "fuel", # Cost
                "tax", "w_tax", "mand_ins", "oil_chg", "tire_chg", "opt_ins", "preloan_cst", "pstloan_cst", "insp_cst", # Maintenance
                "doors", "psngrs", # Capacity
                "ext_l", "ext_w", "ext_h", "int_l", "int_w", "int_h", # Dimensions
                "w_base", "w_track_f", "w_track_r", "grnd_clr", # Terrain Related Dimensions
                "turn_rad", # minimum turn radius
                "weight", # Weight
                "drive", "gears", "trans", # Driving Characteristics
                "eng_mdl", "eng_layout", "cc", "comp_ratio", "comp_type", "kw", "kw_rpm", "trq_nm", "trq_rpm", # Engine Specs
                "w_w_f", "w_ratio_f", "w_cnst_f", "w_rim_f", "w_w_r", "w_ratio_r", "w_cnst_r", "w_rim_r", # Tire Dimensions and Construction
                "brake_f", "brake_r", # Brake Types
                "car_link", "img_link"] # Misc
        d = dict.fromkeys(cols, "-")
        d["car_link"] = car_url
        
        ## ページタイトル ######            
        # DATA: mdl_year
        title = soup.find("title").text
        m = re.search("\s([0-9]{4})年式", title)
        if m:
            d["mdl_year"] = int(m.group(1))

        ## 画像テーブル ######
        # DATA: img_link
        e = soup.find("table", class_="topimg float_L tbl350 font14").find("img")["src"]
        d["img_link"] = e
        # DATA: mfr_year
        e = soup.find("table", class_="topimg float_L tbl350 font14").text
        m = re.search("販売期間：(.*)\s-", e)
        if m:
            d["mfr_year"] = m.group(1)

        ## 説明文 ######
        # DATA: type, gen.
        e = soup.find("p").text
        m = re.search('乗り(.*)代', e).group(1).split("、")
        d["type"] = m[0]
        try:
            d["gen"] = int(m[1])
        except:
            if (m[1] == "初"):
                d["gen"] = 0
            else:
                raise ValueError(f"!!!FATAL: Failed to parse {m[1]} as an integer")
            
        ## 主要諸元テーブル ######
        t1_trs = soup.find("table", class_="tbl350 float_L center line30").find_all("tr")
        for tr in t1_trs[1:]:
            th = tr.find("th").text
            td = tr.find("td")
            # DATA: MULTI
            if (th == "メーカー"):
                # DATA: mfr.
                d["mfr"] = td.text
            elif (th == "車名＆グレード"):
                # DATA: name, grade
                td = td.get_text("@@@").split("@@@")
                d["name"] = td[0]
                d["grade"] = td[1]
            elif (th == "お値段"):
                # DATA: price
                d["price"] = int(td.text.replace("円", ""))
            elif (th == "車両型式"):
                # DATA: mdl
                d["mdl"] = td.text
            elif (th == "駆動方式変速機"):
                # DATA: drive, gears, trans.
                td = td.get_text("@@@").split("@@@")
                drive = td[0].split("・")[0]; d["drive"] = drive
                trans = td[1].split("・")[0]
                if (trans == "（無段変速機）"):
                    d["trans"] = trans
                else:
                    trans = trans.split("速")
                    d["gears"] = int(trans[0])
                    d["trans"] = trans[1]
            elif (th == "ドア/定員"):
                # DATA: doors, psngrs
                td = td.text.split("/")
                d["doors"] = int(td[0][0])
                d["psngrs"] = int(td[1][0])
            elif (th == "車体寸法"):
                # DATA: ext_l, ext_w, ext_h
                td = td.text
                m = re.findall("([0-9]+)", td)
                d["ext_l"] = int(m[0])
                d["ext_w"] = int(m[1])
                d["ext_h"] = int(m[2])
            elif (th == "室内寸法"):
                # DATA: int_l, int_w, int_h
                td = td.text
                m = re.findall("([0-9]+)", td)
                d["int_l"] = int(m[0])
                d["int_w"] = int(m[1])
                d["int_h"] = int(m[2])
            elif (th == "軸距＆輪距"):
                # DATA: w_base, w_track_f, w_track_r
                td = td.get_text("@@@").split("@@@")
                d["w_base"] = int(td[0][:-2])
                f_r = td[1].split("/")
                d["w_track_f"] = int(f_r[0][1:-2])
                d["w_track_r"] = int(f_r[1][1:-2])
            elif (th == "最小半径"):
                # DATA: turn_rad.
                d["turn_rad"] = float(td.text[:-1])
            elif (th == "最低高"):
                # DATA: grnd_clr
                d["grnd_clr"] = int(td.text[:-2])
            elif (th == "タイヤ"):
                tds = td.get_text("@@@").split("@@@")
                for (i, td) in enumerate(tds):
                    # DATA: w_w_f, w_ratio_f, w_cnst_f, w_rim_f
                    # DATA: w_w_r, w_ratio_r, w_cnst_r, w_rim_r
                    m = re.findall("([0-9]+)", td)
                    w = int(m[0])
                    ratio = int(m[1])
                    cnst = re.search('[A-Z]+', td).group(0)
                    rim = int(m[2])
                    d[f"w_w_{'fr'[i]}"] = w
                    d[f"w_ratio_{'fr'[i]}"] = ratio
                    d[f"w_cnst_{'fr'[i]}"] = cnst
                    d[f"w_rim_{'fr'[i]}"] = rim
            elif (th == "ブレーキ"):
                # DATA: brake_f, brake_r
                td = td.get_text("@@@").split("@@@")
                d["brake_f"] = td[0][2:]
                d["brake_r"] = td[1][2:]
            elif (th == "車両重量"):
                # DATA: weight
                d["weight"] = int(re.findall("([0-9]+)", td.text)[0])
                
        ## エンジン諸元テーブル ######
        t1_trs = soup.find("table", class_="tbl350 float_R center line30 mbtm30").find_all("tr")
        for tr in t1_trs[1:-1]:
            th = tr.find("th").text
            td = tr.find("td")
            if (th == "原動機型式"):
                # DATA: eng_mdl.
                d["eng_mdl"] = td.text
            elif (th == "気筒配列"):
                # DATA: eng_layout
                d["eng_layout"] = td.text
            elif (th == "排気量"):
                # DATA: cc
                m = re.findall("([0-9]+)", td.text)
                d["cc"] = int(m[0])
            elif (th == "圧縮比"):
                # DATA: comp_ratio
                d["comp_ratio"] = float(td.text)
            elif (th == "吸気方式"):
                # DATA: comp_type
                d["comp_type"] = td.text
            elif (th == "最高出力"):
                # DATA: kw, kw_rpm
                m = re.findall("([0-9]+)", td.text)
                try:
                    kw = int(m[1])
                    rpm = int(m[2])
                    d["kw"] = kw
                    d["kw_rpm"] = rpm
                except Exception as e:
                    print(f"!!!{e}")
            elif (th == "最大トルク"):
                # DATA: trq_nm, trq_rpm
                m = re.findall("([0-9]+)", td.text)
                nm = int(re.findall("([0-9]*)Nm", td.text)[0])
                rpm = int(m[-1])
                d["trq_nm"] = nm
                d["trq_rpm"] = rpm
            elif (th == "使用燃料"):
                # DATA: fuel
                d["fuel"] = td.text
            elif (th == "JC08燃費"): # Maybe a bit skechy
                # DATA: kmpl
                m = re.search("([0-9]+\.[0-9]+)", td.text).group(1)
                d["kmpl"] = float(m[0])
            elif (th == "100km燃費"): # Maybe a bit skechy
                # DATA: kmpl
                m = re.search("([0-9]+\.[0-9]+)", td.text).group(1)
                l = Decimal(m)
                km = Decimal("100")
                kmpl = round(float(km/l), 2)
                d["kmpl"] = kmpl
            
        ## 維持費テーブル ######
        e = soup.find("table", class_="w100 line30 font16 spnone")
        e = e.get_text("@@@").split("@@@")
        e = [s for s in e if (re.match("[0-9]*円$", s))]
        for (i, p) in enumerate(e):
            p = int(p[:-1])
            if (i == 0):
                # DATA: tax
                d["tax"] = p
            elif (i == 1):
                # DATA: w_tax
                d["w_tax"] = p
            elif (i == 2):
                # DATA: mand_ins
                d["mand_ins"] = p
            elif (i == 4):
                # DATA: oil_chg
                d["oil_chg"] = p
            elif (i == 5):
                # DATA: tire_chg
                d["tire_chg"] = p
            elif (i == 6):
                # DATA: opt_ins
                d["opt_ins"] = p
            elif (i == 9):
                # DATA: preloan_cst
                d["preloan_cst"] = p
            elif (i == 7):
                # DATA: pstloan_cst
                d["pstloan_cst"] = p
            elif (i == 10):
                # DATA: insp_cst
                d["insp_cst"] = p
        #print(d)
        #print(f"{'':=<70}")

        # SQLite
        tup = tuple(d.values())
        try:
            con.execute("""INSERT INTO car(
                mfr, name, type,
                mdl, gen, grade,
                mfr_year, mdl_year,
                price, kmpl, fuel,
                tax, w_tax, mand_ins, oil_chg, tire_chg, opt_ins, preloan_cst, pstloan_cst, insp_cst,
                doors, psngrs,
                ext_l, ext_w, ext_h, int_l, int_w, int_h,
                w_base, w_track_f, w_track_r, grnd_clr,
                turn_rad,
                weight,
                drive, gears, trans,
                eng_mdl, eng_layout, cc, comp_ratio, comp_type, kw, kw_rpm, trq_nm, trq_rpm,
                w_w_f, w_ratio_f, w_cnst_f, w_rim_f, w_w_r, w_ratio_r, w_cnst_r, w_rim_r,
                brake_f, brake_r, car_link, img_link)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            tup)
            con.commit()
        except Exception as e:
            print(e)
            #raise ValueError(e)
        g_sleep(mu,sigma) # 待機スリープ
        ######################################################
        # END: 車一件の詳細ページ
        ######################################################
    print_prog(page, total_pages) # 進行度をプリント
    ######################################################
    # END: 車十件ずつの一覧ページ
    ######################################################
cur.close()
con.close()
