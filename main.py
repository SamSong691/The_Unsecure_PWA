from flask import (
    Flask,
    render_template,
    request,
    redirect,
    make_response,
    session,
    url_for,
)
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from cachelib.file import FileSystemCache
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


SESSION_TYPE = "cachelib"
SESSION_SERIALIZATION_FORMAT = "json"
SESSION_CACHELIB = (
    FileSystemCache(threshold=500, cache_dir=os.path.join(app.root_path, "sessions")),
)


@app.route("/profile", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def profile():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    loginUser = dbUserHandler.getLoginUser()
    if not loginUser:
        return redirect(url_for("home"))

    userProfile = dbUserHandler.getUserProfile(loginUser["id"])
    likedSongs = dbMusicHandler.listAllByIds(userProfile["likedSongs"])
    playList = dbMusicHandler.listAllByIds(userProfile["playList"])
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbUserHandler.insertFeedback(feedback)
        dbUserHandler.listFeedback()
        return render_template(
            "/profile.html.j2",
            loginState=True,
            loginUser=loginUser,
            likedSongs=likedSongs,
            playList=playList,
        )
    else:
        dbUserHandler.listFeedback()
        return render_template(
            "/profile.html.j2",
            loginState=True,
            loginUser=loginUser,
            likedSongs=likedSongs,
            playList=playList,
        )


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


@app.route("/index", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbUserHandler.doLogin(username, password)
        if isLoggedIn:
            return redirect(url_for("profile"))
        else:
            return render_template("/index.html.j2")
    else:
        loginUser = dbUserHandler.getLoginUser()
        if loginUser:
            return redirect(url_for("profile"))
        else:
            return render_template("/index.html.j2")


@app.route("/music", methods=["POST", "GET"])
def musicIndex():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    loginUser = dbUserHandler.getLoginUser()
    musicItems = dbMusicHandler.listAll(loginUser["id"] if loginUser else None)
    return render_template(
        "/music.html.j2", music=musicItems, loginState=(True if loginUser else False)
    )


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


@app.route("/music-new", methods=["POST", "GET"])
def musicNew():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    loginUser = dbUserHandler.getLoginUser()
    msg = ""

    if request.method == "POST":
        if loginUser:
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


@app.route("/music-action", methods=["POST", "GET"])
def musicAction():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    loginUser = dbUserHandler.getLoginUser()
    msg = ""
    if loginUser:
        songId = request.form["id"]
        action = request.form["action"]
        result = dbUserHandler.musicAction(loginUser["id"], songId, action)

        if action == "addLike":
            msg += "[" + songId + "] like " + ("success!" if result else "fail!")
        elif action == "removeLike":
            msg += "[" + songId + "] unlike " + ("success!" if result else "fail!")
        elif action == "addList":
            msg += (
                "[" + songId + "] add into list " + ("success!" if result else "fail!")
            )
        elif action == "removeList":
            msg += (
                "["
                + songId
                + "] remove from list "
                + ("success!" if result else "fail!")
            )
        else:
            msg += "[" + songId + "] can not execute " + action

    return render_template("/music-action.html.j2", msg=msg)


@app.route("/search", methods=["POST", "GET"])
def musicSearch():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    loginUser = dbUserHandler.getLoginUser()

    if request.method == "POST":
        searchKey = request.form["search_key"]
        musicItems = dbMusicHandler.search(
            searchKey, loginUser["id"] if loginUser else None
        )
        return render_template(
            "/search.html.j2",
            search_key=searchKey,
            music=musicItems,
            loginState=(True if loginUser else False),
        )
    else:
        return render_template(
            "/search.html.j2", loginState=(True if loginUser else False)
        )


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config.from_object(__name__)
    Session(app)
    app.run(debug=True, host="0.0.0.0", port=5100)
