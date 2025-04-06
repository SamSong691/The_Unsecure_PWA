import sqlite3 as sql
import re


def listAll(username):
    likedSongs = []
    playList = []

    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    if username:
        row = cur.execute(
            "SELECT username,likedSongs,playList FROM users WHERE username = ?",
            (username,),
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
            "SELECT username,likedSongs,playList FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row[1] and len(row[1]) > 0:
            likedSongs = row[1].split("\n")
        if row[2] and len(row[2]) > 0:
            playList = row[2].split("\n")
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
