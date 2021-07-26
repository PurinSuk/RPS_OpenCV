from enum import unique
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super secret key :)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///players.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    win = db.Column(db.Integer)
    lose = db.Column(db.Integer)
    tie = db.Column(db.Integer)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.win = 0
        self.lose = 0
        self.tie = 0

    def __repr__(self):
        return f"Player({self.username}, win: {self.win}, lose: {self.lose}, tie: {self.tie})"
    

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

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)