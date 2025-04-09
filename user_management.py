from flask import session
import sqlite3 as sql
import time, random, hashlib, html, string


def insertUser(username, password, DoB, email):
    username = html.escape(username, True)
    password = html.escape(password, True)

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
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def doLogin(username, password):
    username = html.unescape(username)
    password = html.unescape(password)

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
            con.close()
            session["loginUser"] = dict(
                id=row[0], name=row[1], status="AUTH_CODE", code=generateCode()
            )
            return True


def doLogout(resp):
    session.pop("loginUser", default=None)


def getLoginUser():
    return session.get("loginUser", None)


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


def musicAction(userId, songId, action):
    songId = int(songId)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT likedSongs,playList FROM users WHERE id = ?", (userId,))
    row = cur.fetchone()
    if row == None:
        con.close()
        return False
    else:
        likedSongs = []
        playList = []

        if row[0] and len(row[0]) > 0:
            likedSongs = [int(x) for x in row[0].split(",")]
        if row[1] and len(row[1]) > 0:
            playList = [int(x) for x in row[1].split(",")]

        if action == "addLike":
            if songId not in likedSongs:
                likedSongs.append(songId)
                cur.execute(
                    "update users set likedSongs=? where id=?",
                    (",".join(str(x) for x in likedSongs), userId),
                )
                con.commit()
                con.close()
            return True
        elif action == "removeLike":
            if songId in likedSongs:
                likedSongs.remove(songId)
                cur.execute(
                    "update users set likedSongs=? where id=?",
                    (",".join(str(x) for x in likedSongs), userId),
                )
                con.commit()
                con.close()
            return True
        elif action == "addList":
            if songId not in playList:
                playList.append(songId)
                cur.execute(
                    "update users set playList=? where id=?",
                    (",".join(str(x) for x in playList), userId),
                )
                con.commit()
                con.close()
            return True
        elif action == "removeList":
            if songId in playList:
                playList.remove(songId)
                cur.execute(
                    "update users set playList=? where id=?",
                    (",".join(str(x) for x in playList), userId),
                )
                con.commit()
                con.close()
            return True
        else:
            return False


def getUserProfile(userId):
    if not userId:
        return False
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT username,numOfComments,likedSongs,playList FROM users WHERE id = ?",
        (userId,),
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
            likedSongs = [int(x) for x in row[2].split(",")]
        if row[3] and len(row[3]) > 0:
            playList = [int(x) for x in row[3].split(",")]

        con.close()
        return dict(
            username=username,
            numOfComments=numOfComments,
            likedSongs=likedSongs,
            playList=playList,
        )


def generateCode(length=6):
    # letters = string.digits
    # result_str = "".join(random.choice(letters) for i in range(length))
    # return result_str
    # for debug
    return "123456"


def verifyCode(code):
    loginUser = getLoginUser()
    if loginUser["status"] == "OK":
        session["loginUser"] = dict(
            id=loginUser["id"], name=loginUser["name"], status="OK"
        )
        return True
    if loginUser["status"] == "AUTH_CODE" and loginUser["code"] == code:
        return True
    return False
