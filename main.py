from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import make_response
import user_management as dbUserHandler
import music_management as dbMusicHandler

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__, static_url_path="/static")


@app.route("/success.html.j2", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbUserHandler.insertFeedback(feedback)
        dbUserHandler.listFeedback()
        return render_template("/success.html.j2", state=True, value="Back")
    else:
        dbUserHandler.listFeedback()
        return render_template("/success.html.j2", state=True, value="Back")


@app.route("/signup", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        email = request.form["email"]
        dbUserHandler.insertUser(username, password, DoB, email)
        return render_template("/index.html.j2")
    else:
        return render_template("/signup.html.j2")


@app.route("/logout", methods=["GET"])
def logout():
    resp = make_response(render_template("logout.html.j2"))
    dbUserHandler.doLogout(resp)
    return resp


# @app.route("/index.html.j2", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbUserHandler.retrieveUsers(username, password)
        if isLoggedIn:
            dbUserHandler.listFeedback()

            resp = make_response(
                render_template("success.html.j2", value=username, state=True)
            )
            dbUserHandler.doLogin(resp, isLoggedIn)
            return resp
        else:
            return render_template("/index.html.j2")
    else:
        username = request.cookies.get("username")
        if username:
            return render_template("success.html.j2", value=username, state=True)
        else:
            return render_template("/index.html.j2")


@app.route("/music", methods=["POST", "GET"])
def musicIndex():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")
    # songId=35
    # songImageFile="/static/images/music/12345.webp"
    # songName="Song1"
    # return render_template("/music/index.html", song_id=songId, song_image_file=songImageFile, song_name=songName)
    # musicDict=[
    #     dict(song_id=35, song_image_file="/static/images/music/12345.webp", song_name="Song1"),
    #     dict(song_id=36, song_image_file="/static/images/music/12345.webp", song_name="Song2")
    # ]
    musicItems = dbMusicHandler.listAll(username)
    return render_template("/music.html.j2", music=musicItems, state=username)


@app.route("/music-action", methods=["POST", "GET"])
def musicAction():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")
    msg = ""
    if username:
        title = request.form["title"]
        action = request.form["action"]
        result = dbUserHandler.musicAction(username, title, action)

        if action == "addLike":
            msg += title + " like " + ("success!" if result else "fail!")
        elif action == "removeLike":
            msg += title + " unlike " + ("success!" if result else "fail!")
        elif action == "addList":
            msg += title + " add into list " + ("success!" if result else "fail!")
        elif action == "removeList":
            msg += title + " remove from list " + ("success!" if result else "fail!")
        else:
            msg += title + " can not execute " + action

    return render_template("/music-action.html.j2", state=username, msg=msg)


@app.route("/search", methods=["POST", "GET"])
def musicSearch():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")

    if request.method == "POST":
        searchKey = request.form["search_key"]
        musicItems = dbMusicHandler.search(username, searchKey)
        return render_template(
            "/search.html.j2",
            search_key=searchKey,
            music=musicItems,
            state=username,
        )
    else:
        return render_template("/search.html.j2", state=username)


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5100)
