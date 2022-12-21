# Import Modules
import re # Regular Expression (Regex)
from time import sleep
import requests
from bs4 import BeautifulSoup

# Import My Modules
from lib.my_modules import gaussian_sleep as g_sleep
from lib.my_modules import print_progress as print_prog

# gaussian_sleep用パラメータ: https://keisan.casio.com/exec/system/1180573188
mu = 7 # 待機時間の平均
sigma = 3 # 待機時間の標準偏差

base_url = "https://rank.greeco-channel.com/access/?pg="

# Requests関連
session = requests.Session() # Sessionを使う事でrequestsに継続性が保たれる(例: Cookie)
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
}
session.headers.update(headers)


# 最初のページにアクセス
res = session.get(base_url) # request.get(url)的な事をする
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

for page in list(range(1, total_pages+1))[:10]: # !!!LIMITER
    ######################################################
    # START: 車十件ずつの一覧ページ
    ######################################################
    # HTTP Request and create Soup
    url = base_url+str(page)
    c = session.get(url).content
    soup = BeautifulSoup(c, 'html.parser')

    # Find all urls for each car
    urls = soup.find("table",class_="rank_tbl").find_all("a")[::2] # [::2]で２ステップにしている(謎の重複しているaタグがあるから)
    urls = [url["href"] for url in urls]    

    for car_url in urls: # !!!LIMITER
        c = session.get(car_url).content
        soup = BeautifulSoup(c, 'html.parser')
        print(car_url)
        ######################################################
        # START: 車一件の詳細ページ
        ######################################################
        # Create an emtpy dict
        cols = ["mfr.", "name", "type", # Common Identifier
                "mod.", "gen.", "grade", # Additional Identifier
                "mfr._year", "mod._year", # Years
                "price", # Cost
                "doors", "psngrs.", # Capacity
                "ext._l", "ext._w", "ext._h", "int._l", "int._w", "int._h", # Dimensions
                "w.base", "w.track_f", "w.track_r", "grnd._clr.", # Terrain Related Dimensions
                "turn_rad.", # minimum turn radius
                "weight", # Weight
                "drive", "gears", "trans.", # Driving Characteristics
                "w._w_f", "w._ratio_f", "w._cnst._f", "w._rim_f", "w._w_r", "w._ratio_r", "w._cnst._r", "w._rim_r", # Tire Dimensions and Construction
                "brake_f", "brake_r", # Brake Types
                "img_link"]
        d = dict.fromkeys(cols, "-")
        
        ## ページタイトル ######            
        # DATA: mod._year
        title = soup.find("title").text
        m = re.search("\s([0-9]{4})年式", title)
        if m:
            d["mod._year"] = int(m.group(1))

        ## 画像テーブル ######
        # DATA: img_link
        e = soup.find("table", class_="topimg float_L tbl350 font14").find("img")["src"]
        d["img_link"] = e
        # DATA: mfr._year
        e = soup.find("table", class_="topimg float_L tbl350 font14").text
        m = re.search("販売期間：(.*)\s-", e)
        if m:
            d["mfr._year"] = m.group(1)

        ## 説明文 ######
        # DATA: type, gen.
        e = soup.find("p").text
        m = re.search('乗り(.*)代', e).group(1).split("、")
        d["type"] = m[0]
        try:
            d["gen."] = int(m[1])
        except:
            if (m[1] == "初"):
                d["gen."] = 0
            else:
                raise ValueError(f"!!!FATAL: Failed to parse {m[1]} as an integer.")
            
        ## 主要諸元テーブル ######
        t1_trs = soup.find("table", class_="tbl350 float_L center line30").find_all("tr")
        for (i, tr) in enumerate(t1_trs[1:]):
            th = tr.find("th").text
            td = tr.find("td")
            # DATA: MULTI
            if (th == "メーカー"):
                # DATA: mfr.
                d["mfr."] = td.text
            elif (th == "車名＆グレード"):
                # DATA: name, grade
                td = td.get_text("@@@").split("@@@")
                d["name"] = td[0]
                d["grade"] = td[1]
            elif (th == "お値段"):
                # DATA: price
                d["price"] = int(td.text.replace("円", ""))
            elif (th == "車両型式"):
                # DATA: mod.
                d["mod."] = td.text
            elif (th == "駆動方式変速機"):
                # DATA: drive, gears, trans.
                td = td.get_text("@@@").split("@@@")
                drive = td[0].split("・")[0]; d["drive"] = drive
                trans = td[1].split("・")[0]
                if (trans == "（無段変速機）"):
                    d["trans."] = trans
                else:
                    trans = trans.split("速")
                    d["gears"] = int(trans[0])
                    d["trans."] = trans[1]
            elif (th == "ドア/定員"):
                # DATA: doors, psngrs.
                td = td.text.split("/")
                d["doors"] = int(td[0][0])
                d["psngrs."] = int(td[1][0])
            elif (th == "車体寸法"):
                # DATA: ext._l, ext._w, ext._h
                td = td.text
                m = re.findall("([0-9]+)", td)
                d["ext._l"] = int(m[0])
                d["ext._w"] = int(m[1])
                d["ext._h"] = int(m[2])
            elif (th == "室内寸法"):
                # DATA: int._l, int._w, int._h
                td = td.text
                m = re.findall("([0-9]+)", td)
                d["int._l"] = int(m[0])
                d["int._w"] = int(m[1])
                d["int._h"] = int(m[2])
            elif (th == "軸距＆輪距"):
                # DATA: w.base, w.track_f, w.track_r
                td = td.get_text("@@@").split("@@@")
                d["w.base"] = int(td[0][:-2])
                f_r = td[1].split("/")
                d["w.track_f"] = int(f_r[0][1:-2])
                d["w.track_r"] = int(f_r[1][1:-2])
            elif (th == "最小半径"):
                # DATA: turn_rad.
                d["turn_rad."] = float(td.text[:-1])
            elif (th == "最低高"):
                # DATA: grnd._clr
                d["grnd._clr."] = int(td.text[:-2])
            elif (th == "タイヤ"):
                tds = td.get_text("@@@").split("@@@")
                for (i, td) in enumerate(tds):
                    # DATA: w._w_f, w._ratio_f, w._cnst._f, w._rim_f
                    # DATA: w._w_r, w._ratio_r, w._cnst._r, w._rim_r
                    m = re.findall("([0-9]+)", td)
                    w = int(m[0])
                    ratio = int(m[1])
                    cnst = re.search('[A-Z]+', td).group(0)
                    rim = int(m[2])
                    d[f"w._w_{'fr'[i]}"] = w
                    d[f"w._ratio_{'fr'[i]}"] = ratio
                    d[f"w._cnst._{'fr'[i]}"] = cnst
                    d[f"w._rim_{'fr'[i]}"] = rim
            elif (th == "ブレーキ"):
                # DATA: brake_f, brake_r
                td = td.get_text("@@@").split("@@@")
                d["brake_f"] = td[0][2:]
                d["brake_r"] = td[1][2:]
            elif (th == "車両重量"):
                # DATA: weight
                d["weight"] = int(re.findall("([0-9]+)", td.text)[0])
                
        ## エンジン諸元テーブル ######
        print(f"{'--Engine Table':-<40}")
        t1_trs = soup.find("table", class_="tbl350 float_R center line30 mbtm30").find_all("tr")
        for (i, tr) in enumerate(t1_trs[1:-1]):
            th = tr.find("th").text
            td = tr.find("td").text
            print(th, td)

        print(d)
        print(f"{'':=<70}")
        g_sleep(mu,sigma) # 待機スリープ
        ######################################################
        # END: 車一件の詳細ページ
        ######################################################
    print_prog(page, total_pages) # 進行度をプリント
    ######################################################
    # END: 車十件ずつの一覧ページ
    ######################################################
