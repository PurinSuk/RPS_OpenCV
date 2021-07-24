from flask import Flask, render_template, url_for, request, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key :)"

@app.route("/home/")
def home():
    if "username" in session:
        return render_template("home.html", user=session["username"])
    else:
        return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        username = request.form["username"]
        password = request.form["password"]

        session["username"] = username
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)