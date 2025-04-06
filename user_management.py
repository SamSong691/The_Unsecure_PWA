import sqlite3 as sql
import time
import random
import hashlib


def insertUser(username, password, DoB, email):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth,email) VALUES (?,?,?,?)",
        (username, encryptPassword(password), DoB, email),
    )
    con.commit()
    con.close()


def encryptPassword(password):
    salt = "gW#g@sY*W.3445"
    return hashlib.md5((salt + password).encode("utf-8")).hexdigest()


def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    # parameterized query
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cur.fetchone() == None:
        con.close()
        return False
    else:
        cur.execute(
            "SELECT * FROM users WHERE username = ? and password = ?",
            (username, encryptPassword(password)),
        )
        # Plain text log of visitor count as requested by Unsecure PWA management
        with open("visitor_log.txt", "r") as file:
            number = int(file.read().strip())
            number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))
        # Simulate response time of heavy app for testing purposes
        time.sleep(random.randint(80, 90) / 1000)
        row = cur.fetchone()
        if row == None:
            con.close()
            return False
        else:
            username = row[1]
            con.close()
            return username


def doLogin(resp, username):
    resp.set_cookie("username", username)


def doLogout(resp):
    resp.set_cookie("username", "", expires=0)


def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()


def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")
        f.write("</p>\n")
    f.close()


def musicAction(username, title, action):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT likedSongs,playList FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if row == None:
        con.close()
        return False
    else:
        likedSongs = []
        playList = []

        if row[0] and len(row[0]) > 0:
            likedSongs = row[0].split("\n")
        if row[1] and len(row[1]) > 0:
            playList = row[1].split("\n")

        if action == "addLike":
            if title not in likedSongs:
                likedSongs.append(title)
                cur.execute(
                    "update users set likedSongs=? where username=?",
                    ("\n".join(likedSongs), username),
                )
                con.commit()
                con.close()
            return True
        elif action == "removeLike":
            if title in likedSongs:
                likedSongs.remove(title)
                cur.execute(
                    "update users set likedSongs=? where username=?",
                    ("\n".join(likedSongs), username),
                )
                con.commit()
                con.close()
            return True
        elif action == "addList":
            if title not in playList:
                playList.append(title)
                cur.execute(
                    "update users set playList=? where username=?",
                    ("\n".join(playList), username),
                )
                con.commit()
                con.close()
            return True
        elif action == "removeList":
            if title in playList:
                playList.remove(title)
                cur.execute(
                    "update users set playList=? where username=?",
                    ("\n".join(playList), username),
                )
                con.commit()
                con.close()
            return True
        else:
            return False


def getUserProfile(username):
    if not username:
        return False
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT username,numOfComments,likedSongs,playList FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    if row == None:
        con.close()
        return False
    else:
        username = row[0]
        numOfComments = row[1]
        likedSongs = []
        playList = []
        if row[2] and len(row[2]) > 0:
            likedSongs = row[2].split("\n")
        if row[3] and len(row[3]) > 0:
            playList = row[3].split("\n")

        con.close()
        return dict(
            username=username,
            numOfComments=numOfComments,
            likedSongs=likedSongs,
            playList=playList,
        )
