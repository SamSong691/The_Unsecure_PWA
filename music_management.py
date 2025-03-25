import sqlite3 as sql

def getSongCategory():
    return ["Pop", "Country"]

def listAll():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("select id,song_name,artist,song_image_filename,category from musics order by id desc").fetchall()
    con.close()
    musicList = []
    for row in data:
        musicList.append(dict(id=row[0], song_name=row[1], artist=row[2], song_image_filename=row[3], category=row[4]))
    print(musicList)
    return musicList

def search(key):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute(f"select id,song_name,artist,song_image_filename,category from musics where song_name like '%{key}%' or artist like '%{key}%' or category like '%{key}%'").fetchall()
    con.close()
    musicList = []
    for row in data:
        musicList.append(dict(id=row[0], song_name=row[1], artist=row[2], song_image_filename=row[3], category=row[4]))
    return musicList
