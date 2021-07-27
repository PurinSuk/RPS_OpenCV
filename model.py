from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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