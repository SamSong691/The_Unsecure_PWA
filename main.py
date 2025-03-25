from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import user_management as dbUserHandler
import music_management as dbMusicHandler

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__, static_url_path="/static")


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbUserHandler.insertFeedback(feedback)
        dbUserHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbUserHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        dbUserHandler.insertUser(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
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
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")

@app.route("/music.html", methods=["POST", "GET"])
def musicIndex():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    # songId=35
    # songImageFile="/static/images/music/12345.webp"
    # songName="Song1"
    # return render_template("/music/index.html", song_id=songId, song_image_file=songImageFile, song_name=songName)
    # musicDict=[
    #     dict(song_id=35, song_image_file="/static/images/music/12345.webp", song_name="Song1"),
    #     dict(song_id=36, song_image_file="/static/images/music/12345.webp", song_name="Song2")
    # ]
    musicItems =dbMusicHandler.listAll()
    return render_template("/music.html", music=musicItems)

@app.route("/search.html", methods=["POST", "GET"])
def musicSearch():
    print("request.method="+request.method)
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        searchKey = request.form["search_key"]
        print("searchKey="+searchKey)
        musicItems=dbMusicHandler.search(searchKey)
        print("musicItems=")
        print(musicItems)
        return render_template("/search.html", search_key=searchKey, music=musicItems)
    else:
        return render_template("/search.html")

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5100)
