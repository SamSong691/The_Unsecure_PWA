import sqlite3 as sql
import re, html


def listAll(userId=None):
    likedSongs = []
    playList = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    if userId:
        row = cur.execute(
            "SELECT username,likedSongs,playList FROM users WHERE id = ?",
            (userId,),
        ).fetchone()
        if row[1] and len(row[1]) > 0:
            likedSongs = [int(x) for x in row[1].split(",")]
        if row[2] and len(row[2]) > 0:
            playList = [int(x) for x in row[2].split(",")]

    data = cur.execute(
        "select id,title,artist,song_image_filename,genre,album,duration from musics order by id desc"
    ).fetchall()

    con.close()
    musicList = []
    for row in data:
        musicList.append(
            dict(
                id=row[0],
                title=html.unescape(row[1]),
                artist=html.unescape(row[2]),
                song_image_filename=row[3],
                genre=html.unescape(row[4]),
                album=html.unescape(row[5]),
                duration=secondsToStr(row[6]),
                isLiked=(row[0] in likedSongs),
                inPlayList=(row[0] in playList),
            )
        )
    return musicList


def listAllByIds(ids):
    list = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    print(",".join(str(x) for x in ids))
    data = cur.execute(
        "select id,title from musics where id in ("
        + ",".join(str(x) for x in ids)
        + ")"
    ).fetchall()
    for row in data:
        list.append(
            dict(
                id=row[0],
                title=html.unescape(row[1]),
            )
        )

    return list


def secondsToStr(seconds):
    hours = seconds // 3600
    remain = seconds % 3600
    mins = remain // 60
    secs = remain % 60
    if hours > 0:
        return f"{hours}:{mins}:{secs}"
    else:
        return f"{mins}:{secs}"


def search(key, userId=None):
    likedSongs = []
    playList = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    if userId:
        row = cur.execute(
            "SELECT username,likedSongs,playList FROM users WHERE id = ?",
            (userId,),
        ).fetchone()
        if row[1] and len(row[1]) > 0:
            likedSongs = [int(x) for x in row[1].split(",")]
        if row[2] and len(row[2]) > 0:
            playList = [int(x) for x in row[2].split(",")]
    searchKey = "%" + key + "%"
    data = cur.execute(
        "select id,title,artist,song_image_filename,genre,album,duration from musics where title like ? or artist like ? or genre like ?",
        (searchKey, searchKey, searchKey),
    ).fetchall()
    con.close()
    musicList = []
    for row in data:
        musicList.append(
            dict(
                id=row[0],
                title=html.unescape(row[1]),
                artist=html.unescape(row[2]),
                song_image_filename=row[3],
                genre=html.unescape(row[4]),
                album=html.unescape(row[5]),
                duration=secondsToStr(row[6]),
                isLiked=(row[0] in likedSongs),
                inPlayList=(row[0] in playList),
            )
        )
    return musicList


def newRecord(data):
    if not data["song_image_filename"]:
        raise AssertionError("Image file upload failed")
    if len(data["title"]) < 5 or len(data["title"]) > 50:
        raise AssertionError("Title must be between 5 and 50 characters")
    if len(data["artist"]) < 2 or len(data["artist"]) > 50:
        raise AssertionError("Artist must be between 2 and 50 characters")
    if len(data["genre"]) < 5 or len(data["genre"]) > 50:
        raise AssertionError("Genre must be between 5 and 50 characters")
    if len(data["album"]) < 2 or len(data["album"]) > 50:
        raise AssertionError("Album must be between 2 and 50 characters")
    if not re.search("[0-9]+", data["duration"]):
        raise AssertionError("Duration must be a positive number")

    title = html.escape(title, True)
    artist = html.escape(artist, True)
    genre = html.escape(genre, True)
    album = html.escape(album, True)

    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO musics (title,artist,genre,album,duration,song_image_filename) VALUES (?,?,?,?,?,?)",
        (
            data["title"],
            data["artist"],
            data["genre"],
            data["album"],
            data["duration"],
            data["song_image_filename"],
        ),
    )
    con.commit()
    con.close()

    return True
