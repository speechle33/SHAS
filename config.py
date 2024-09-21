import os
#import redis Если больше не нужен, импорт можно убрать

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Убрано использование Redis
    SESSION_TYPE = 'filesystem'  # Используем сессии на файловой системе вместо Redis
    SESSION_FILE_DIR = os.path.join(basedir, 'flask_sessions')  # Папка для хранения сессионных файлов
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # Убрано использование Redis
    # SESSION_REDIS = redis.from_url('redis://localhost:6379')