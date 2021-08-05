from flask import Flask, render_template, url_for, request, redirect, session, flash, Response
from model import db, Player
import cv2
from HandTrackingModule import handDetector
from enum import Enum

class Choice(Enum):
    rock = 0
    paper = 1
    scissors = 2

app = Flask(__name__)
app.secret_key = "super secret key :)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///players.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

camera = cv2.VideoCapture(0)

player_choice = None
tipsId = [8, 12, 16, 20]

rps_images = [cv2.resize(cv2.imread("static/rock_rps.png"), (111, 113), interpolation=cv2.INTER_AREA),
              cv2.resize(cv2.imread("static/paper_rps.png"), (111, 113), interpolation=cv2.INTER_AREA),
              cv2.resize(cv2.imread("static/scissors_rps.png"), (111, 113), interpolation=cv2.INTER_AREA)]

def gen_frames():
    global player_choice
    detector = handDetector()
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            """
            Check and update the global variable (rock/ paper/ scissors/ not_valid) 
            """
            lmList = detector.findPosition(frame)
            if len(lmList) == 0:
                continue
            # check four non-thumb fingers
            non_thumbs = [1 if lmList[i][2] < lmList[i-2][2] else 0 for i in tipsId]
            if non_thumbs == [0, 0, 0, 0]:
                player_choice = Choice.rock
            elif non_thumbs == [1, 1, 0, 0]:
                player_choice = Choice.scissors
            elif non_thumbs == [1, 1, 1, 1]:
                player_choice = Choice.paper

            # right hand
            if lmList[1][1] < lmList[17][1] and player_choice is not None:
                if lmList[3][1] >= lmList[4][1] and (player_choice is Choice.rock or player_choice is Choice.scissors):
                    player_choice = None
                elif lmList[3][1] < lmList[4][1] and player_choice is Choice.paper:
                    player_choice = None
            # left hand
            elif lmList[1][1] > lmList[17][1] and player_choice is not None:
                if lmList[3][1] < lmList[4][1] and (player_choice is Choice.rock or player_choice is Choice.scissors):
                    player_choice = None
                elif lmList[3][1] >= lmList[4][1] and player_choice is Choice.paper:
                    player_choice = None
            else:
                player_choice = None

            if player_choice is not None:
                # show image of player_choice on frame
                frame[:113, :111] = rps_images[player_choice.value]

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
            query = Player.query.filter_by(username=username, password=password).first()
            if query is not None:
                session["username"] = username
                session["win"] = query.win
                session["lose"] = query.lose
                session["draw"] = query.tie
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
        """
        Code to determine the values to pass to game.html
        """
        return render_template("game.html", game_result="You Lose!", player_choice="none.jpg", bot_choice="paper_rps.png",
                               win=session["win"], lose=session["lose"], draw=session["draw"])
    return redirect(url_for("login"))

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/play/")
def play():
    if "username" in session:
        return render_template("play.html")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)