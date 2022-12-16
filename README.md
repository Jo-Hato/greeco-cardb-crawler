# greeco-cardb-crawler
An experimental tutorial Python web crawler project using requests.get() and BeautifulSoup4 for crawling a car database written in Japanese.
This project isn't meant for public use, but for in-school face-to-face teaching.

# 環境構築手順
## git cloneの手順
1. 任意のディレクトリ内(e.g. Git_clone/)で`git clone https://github.com/Jo-Hato/greeco-cardb-crawler`でリポジトリをクローンする

## Conda環境構築
1. `conda list`既存環境を確認する
2. (if 希望の環境 not exists)`python3 --version`でPythonのバージョン確認
3. `conda create -n "環境名" python=3.x.xx`で環境を構築する
4. `conda activate 環境名`で環境に入る。(base) -> (環境名)に変化する事を確認する
5. 環境内で`pip install -r requirements.txt`で依存パッケージをインストールする

# クローリング実行
1. `python crawler.py`で実行する
