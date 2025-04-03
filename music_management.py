import sqlite3 as sql


def listAll(username):
    likedSongs = []
    playList = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    if username:
        row = cur.execute(
            f"SELECT username,likedSongs,playList FROM users WHERE username = '{username}'"
        ).fetchone()
        if row[1] and len(row[1]) > 0:
            likedSongs = row[1].split("\n")
        if row[2] and len(row[2]) > 0:
            playList = row[2].split("\n")

    data = cur.execute(
        "select id,title,artist,song_image_filename,genre,album,duration from musics order by id desc"
    ).fetchall()

    con.close()
    musicList = []
    for row in data:
        musicList.append(
            dict(
                id=row[0],
                title=row[1],
                artist=row[2],
                song_image_filename=row[3],
                genre=row[4],
                album=row[5],
                duration=secondsToStr(row[6]),
                isLiked=(row[1] in likedSongs),
                inPlayList=(row[1] in playList),
            )
        )
    print(musicList)
    return musicList


def secondsToStr(seconds):
    hours = seconds // 3600
    remain = seconds % 3600
    mins = remain // 60
    secs = remain % 60
    if hours > 0:
        return f"{hours}:{mins}:{secs}"
    else:
        return f"{mins}:{secs}"


def search(username, key):
    likedSongs = []
    playList = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    if username:
        row = cur.execute(
            f"SELECT username,likedSongs,playList FROM users WHERE username = '{username}'"
        ).fetchone()
        if row[1] and len(row[1]) > 0:
            likedSongs = row[1].split("\n")
        if row[2] and len(row[2]) > 0:
            playList = row[2].split("\n")

    data = cur.execute(
        f"select id,title,artist,song_image_filename,genre,album,duration from musics where title like '%{key}%' or artist like '%{key}%' or genre like '%{key}%'"
    ).fetchall()
    con.close()
    musicList = []
    for row in data:
        musicList.append(
            dict(
                id=row[0],
                title=row[1],
                artist=row[2],
                song_image_filename=row[3],
                genre=row[4],
                album=row[5],
                duration=secondsToStr(row[6]),
                isLiked=(row[1] in likedSongs),
                inPlayList=(row[1] in playList),
            )
        )
    return musicList
