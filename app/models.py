from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login

MAX_PLAYERS = 20

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    nickname = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Integer, default=10000, nullable=False)  # Убедитесь, что тип данных тут Integer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games = db.relationship('Game', backref='player', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def place_bet(self, amount):
        if amount > self.balance:
            raise ValueError("Bet exceeds balance")
        self.balance -= amount
        return amount

    def receive_winnings(self, amount):
        self.balance += amount

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Game {self.id}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))