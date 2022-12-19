# Import Modules
import re # Regular Expression (Regex)
from time import sleep
import requests
from bs4 import BeautifulSoup

# Import My Modules
from lib.my_modules import gaussian_sleep as g_sleep
from lib.my_modules import print_progress as print_prog

# gaussian_sleep用パラメータ: https://keisan.casio.com/exec/system/1180573188
mu = 3 # 待機時間の平均
sigma = 1 # 待機時間の標準偏差

base_url = "https://rank.greeco-channel.com/access/?pg="

# Requests関連
session = requests.Session() # Sessionを使う事でrequestsに継続性が保たれる(例: Cookie)
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
}
session.headers.update(headers)


# 最初のページにアクセス
res = session.get(base_url) # request.get(url)的な事をする
print(res.status_code) # ステータスコードを表示する
c = res.content # 変数名: c = content
soup = BeautifulSoup(c, 'html.parser') # Soupを作る

# 最初のページからこれから取得するデータの概要を取得する
s = soup.find("div", class_="theContentWrap-ccc").find_all("p")[4].text # tag内のtextを取り出す
total_cars = int(re.search(r"全(.*?)件", s).group(1)) # Regexを使ってDBに登録されている車の総数を取り出す
total_pages= int(re.search(r"・(.*?)ページ中", s).group(1)) # Regexを使って総ページ数を取り出す
print("Total Cars: {}, Total Pages: {}".format(total_cars, total_pages))

for page in list(range(1, total_pages+1))[:3]:
    url = base_url+str(page)
    c = session.get(url).content
    soup = BeautifulSoup(c, 'html.parser')
    urls = soup.find("table",class_="rank_tbl").find_all("a")[::2] # [::2]で２ステップにしている(謎の重複しているaタグがあるから)
    urls = [url["href"] for url in urls]
    for car_url in urls:
        c = session.get(car_url).content
        soup = BeautifulSoup(c, 'html.parser')
        ######################################################
        ######################################################
        # ページタイトル
        print(soup.find("title").text)

        # 主要諸元テーブル
        t1_trs = soup.find("table", class_="tbl350 float_L center line30").find_all("tr")
        for (i, tr) in enumerate(t1_trs):
            th = tr.find("th").text
            if (i != 0):
                td = tr.find("td").text
                print(th, td)
                
        # エンジン諸元テーブル
        t1_trs = soup.find("table", class_="tbl350 float_R center line30 mbtm30").find_all("tr")
        for (i, tr) in enumerate(t1_trs[:-1]):
            th = tr.find("th").text
            if (i != 0):
                td = tr.find("td").text
                print(th, td)
                
        g_sleep(mu,sigma) # 待機スリープ
        ######################################################
        ######################################################
    print_prog(page, total_pages) # 進行度をプリント
    g_sleep(mu, sigma) # 待機スリープ
