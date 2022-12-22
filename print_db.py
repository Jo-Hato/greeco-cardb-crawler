import sqlite3 as sl # SQLite3を"sl"という名前でインポートする。

db_name = "car.db"
con = sl.connect(db_name)
cur = con.cursor()

res = con.execute("SELECT * FROM car").fetchall() # Tips: resは恐らくresponse(返答)かresult(結果)の略。また、「*」は全選択を意味する。

print(res) # resを確認する。
print(len(res))
print(type(res)) # タイプを確認する。
print() # ただの改行。

for rec in res:
    print(rec)
cur.close()
con.close()
