from flask import Flask, render_template, url_for, request, redirect, session, flash, Response
from model import db, Player
import cv2

app = Flask(__name__)
app.secret_key = "super secret key :)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///players.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.before_first_request
def initialise_database():
    db.create_all()

@app.route("/home/")
def home():
    if "username" in session:
        return render_template("home.html", user=session["username"])
    else:
        return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Ensure that the user completes the form
        if "login" not in request.form or request.form["username"] == "" or\
            request.form["password"] == "":
            flash("Please complete the form!", "error")
            return redirect(url_for("login"))

        # Variables to hold user's information
        login = request.form["login"]
        username = request.form["username"]
        password = request.form["password"]

        # Check sign in or register
        if login == "signin":
            if Player.query.filter_by(username=username, password=password).first() is not None:
                session["username"] = username
                return redirect(url_for("home"))
            else:
                flash("Username or password (or both) is incorrect!", "error")
                return redirect(url_for("login"))
        # Case register
        else:
            # validate username and password here
            if Player.query.filter_by(username=username).first() is not None:
                flash("This username has already been used!", "error")
                return redirect(url_for("login"))

            # Create a new user and add them to the database
            player = Player(username, password)
            db.session.add(player)
            db.session.commit()
            flash("Register successfully!", "info")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/game/")
def game():
    if "username" in session:
        return render_template("game.html")
    return redirect(url_for("login"))

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/play/")
def play():
    return render_template("play.html")

if __name__ == "__main__":
    app.run()