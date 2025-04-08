from flask import Flask, render_template, request, redirect, make_response
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import os
import user_management as dbUserHandler
import music_management as dbMusicHandler

# Code snippet for logging a message
# app.logger.critical("message")

UPLOAD_FOLDER = "/static/images/music"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.urandom(24)
csrf = CSRFProtect(app)


@app.route("/profile.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")
    userProfile = dbUserHandler.getUserProfile(username)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbUserHandler.insertFeedback(feedback)
        dbUserHandler.listFeedback()
        return render_template(
            "/profile.html.j2", loginState=username, userProfile=userProfile
        )
    else:
        dbUserHandler.listFeedback()
        return render_template(
            "/profile.html.j2", loginState=username, userProfile=userProfile
        )


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
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


@app.route("/logout.html", methods=["GET"])
def logout():
    resp = make_response(render_template("logout.html.j2"))
    dbUserHandler.doLogout(resp)
    return resp


@app.route("/index.html", methods=["POST", "GET"])
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
            userProfile = dbUserHandler.getUserProfile(username)
            dbUserHandler.listFeedback()

            resp = make_response(
                render_template(
                    "profile.html.j2", loginState=isLoggedIn, userProfile=userProfile
                )
            )
            dbUserHandler.doLogin(resp, isLoggedIn)
            return resp
        else:
            return render_template("/index.html.j2")
    else:
        username = request.cookies.get("username")
        if username:
            userProfile = dbUserHandler.getUserProfile(username)
            return render_template(
                "profile.html.j2", loginState=username, userProfile=userProfile
            )
        else:
            return render_template("/index.html.j2")


@app.route("/music.html", methods=["POST", "GET"])
def musicIndex():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")
    musicItems = dbMusicHandler.listAll(username)
    return render_template("/music.html.j2", music=musicItems, loginState=username)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def getUploadedFile(uploadedFile):
    if uploadedFile and allowed_file(uploadedFile.filename):
        filename = secure_filename(uploadedFile.filename)
        uploadedFile.save(
            os.path.join(
                os.path.dirname(app.instance_path) + app.config["UPLOAD_FOLDER"],
                filename,
            )
        )
        return filename
        # return os.path.join(app.config["UPLOAD_FOLDER"], filename)
    else:
        return False


@app.route("/music-new.html", methods=["POST", "GET"])
def musicNew():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    username = request.cookies.get("username")
    msg = ""

    if request.method == "POST":
        if username:
            item = dict(
                title=request.form["title"],
                artist=request.form["artist"],
                song_image_filename=getUploadedFile(request.files["image"]),
                genre=request.form["genre"],
                album=request.form["album"],
                duration=request.form["duration"],
            )
            try:
                dbMusicHandler.newRecord(item)
                return render_template("/music-new.html.j2", msg="New item success!")
            except AssertionError as e:
                return render_template("/music-new.html.j2", msg=str(e))


@app.route("/music-action.html", methods=["POST", "GET"])
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
            msg += "[" + title + "] like " + ("success!" if result else "fail!")
        elif action == "removeLike":
            msg += "[" + title + "] unlike " + ("success!" if result else "fail!")
        elif action == "addList":
            msg += (
                "[" + title + "] add into list " + ("success!" if result else "fail!")
            )
        elif action == "removeList":
            msg += (
                "["
                + title
                + "] remove from list "
                + ("success!" if result else "fail!")
            )
        else:
            msg += "[" + title + "] can not execute " + action

    return render_template("/music-action.html.j2", loginState=username, msg=msg)


@app.route("/search.html", methods=["POST", "GET"])
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
            loginState=username,
        )
    else:
        return render_template("/search.html.j2", loginState=username)


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.run(debug=True, host="0.0.0.0", port=5100)
