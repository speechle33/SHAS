from datetime import datetime
from app import db # Импорт объекта базы данных из приложения
from flask_login import UserMixin # Миксин для управления пользователями с Flask-Login
from app import login # Импорт объекта login из вашего приложения

MAX_PLAYERS = 10

# Определение модели пользователя
class User(db.Model, UserMixin):
	# Модель пользователя, представляющая зарегистрированного участника игры.
    # Наследуется от db.Model для взаимодействия с базой данных и от UserMixin для интеграции с Flask-Login.
    id = db.Column(db.Integer, primary_key=True) # Уникальный идентификатор пользователя
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Integer, default=10000, nullable=False)# Баланс пользователя, по умолчанию 10 000
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Дата и время создания пользователя
    games = db.relationship('Game', backref='player', lazy='dynamic') # Связь с играми пользователя


    def __repr__(self):
        return f'<User {self.username}>'
#Возвращает строковое представление объекта пользователя для отладки.
    def place_bet(self, amount): #Метод для размещения ставки пользователем.
        if amount > self.balance:
            raise ValueError("Bet exceeds balance") # Выбрасывает исключение, если ставка превышает баланс
        self.balance -= amount  # Вычитает сумму ставки из баланса пользователя
        return amount # Возвращает сумму ставки

    def receive_winnings(self, amount):
        # Метод для зачисления выигрыша пользователю
		self.balance += amount # Добавляет сумму выигрыша к балансу пользователя

# Определение модели игры
class Game(db.Model):
    #Модель игры, представляющая отдельную игровую сессию пользователя.
	id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Внешний ключ, связывающий игру с пользователем
    state = db.Column(db.JSON, nullable=False) # Состояние игры в формате JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Game {self.id}>'

# Функция загрузки пользователя по идентификатору для Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))