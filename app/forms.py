# импорт необходимых классов из Flask-WTF и WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from app.models import User

# Форма для входа пользователя
class LoginForm(FlaskForm):
    # Поле для ввода имени пользователя, обязательное для заполнения
	username = StringField('Username', validators=[DataRequired()])
    # Поле для ввода пароля, обязательное для заполнения
	password = PasswordField('Password', validators=[DataRequired()])
    # Флажок "Запомнить меня" для сохранения сессии
	remember_me = BooleanField('Remember Me')
    # Кнопка отправки формы
	submit = SubmitField('Sign In')
	
# Форма для регистрации нового пользователя
class RegistrationForm(FlaskForm):
     # Поле для ввода имени пользователя, обязательное для заполнения
	username = StringField('Username', validators=[DataRequired()])
    # Поле для ввода электронной почты, обязательное и должно соответствовать формату email
	email = StringField('Email', validators=[DataRequired(), Email()])
    # Поле для ввода пароля, обязательное для заполнения
	password = PasswordField('Password', validators=[DataRequired()])
    # Поле для повторного ввода пароля, обязательное и должно совпадать с полем 'password'
	password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    # Кнопка отправки формы
	submit = SubmitField('Register')

    # Валидатор для проверки уникальности имени пользователя
	def validate_username(self, username):
        # Поиск пользователя с введенным именем
		user = User.query.filter_by(username=username.data).first()
        if user is not None:
            # Если такой пользователь существует, то ошибка валидации
			raise ValidationError('Please use a different username.')

     # Валидатор для проверки уникальности электронной почты
	def validate_email(self, email):
        # Поиск пользователя с введенной электронной почтой
		user = User.query.filter_by(email=email.data).first()
        if user is not None:
            # Если такой пользователь существует, то ошибка валидации
			raise ValidationError('Please use a different email address.')

# Форма для размещения ставки в игре
class BetForm(FlaskForm):
    # Поле для ввода суммы ставки, обязательное и должно быть не менее 1
	bet_amount = IntegerField('Bet Amount', validators=[DataRequired(), NumberRange(min=1)])
    # Кнопка отправки формы
	submit = SubmitField('Place Bet')

# Форма для удаления пользователя
class DeleteUserForm(FlaskForm):
    # Поле для ввода имени пользователя, которого нужно удалить, обязательное для заполнения
	username = StringField('Username', validators=[DataRequired()])
    # Кнопка отправки формы
	submit = SubmitField('Delete User')

    # Валидатор для проверки существования пользователя с введенным именем
	def validate_username(self, username):
        # Поиск пользователя по имени
		user = User.query.filter_by(username=username.data).first()
        if user is None:
            # Если пользователь не найден, то ошибка валидации
			raise ValidationError('User not found.')

# Форма для выбора пользователя для входа
class SelectUserForm(FlaskForm):
    # Выпадающий список для выбора пользователя по его ID, преобразует значение в целое число
	user_id = SelectField('Select User', coerce=int)
    # Кнопка отправки формы
	submit = SubmitField('Select User')

    # Инициализация формы, заполняет выпадающий список пользователями из базы данных
	def __init__(self, *args, **kwargs):
        super(SelectUserForm, self).__init__(*args, **kwargs)
        # Заполнение вариантов выбора пользователями с отображением их баланса
		self.user_id.choices = [(user.id, f"{user.username} (Balance: {user.balance})") for user in User.query.all()]

# Форма для подтверждения удаления пользователя
class ConfirmDeleteForm(FlaskForm):
    # Кнопка подтверждения удаления
	confirm = SubmitField('Yes')
    # Кнопка отмены удаления
	cancel = SubmitField('No')