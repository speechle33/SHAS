from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user is not None:
            raise ValidationError('Please use a different nickname.')

class BetForm(FlaskForm):
    bet_amount = IntegerField('Bet Amount', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Place Bet')

class DeleteUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Delete User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('User not found.')

class SelectUserForm(FlaskForm):
    user_id = SelectField('Select User', coerce=int)
    submit = SubmitField('Select User')

    def __init__(self, *args, **kwargs):
        super(SelectUserForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(user.id, f"{user.nickname} (Balance: {user.balance})") for user in User.query.all()]

class ConfirmDeleteForm(FlaskForm):
    confirm = SubmitField('Yes')
    cancel = SubmitField('No')