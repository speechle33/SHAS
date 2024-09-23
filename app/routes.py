from flask import g, Blueprint, render_template, flash, redirect, url_for, session, request, jsonify, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Game
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from app.forms import (
    LoginForm, RegistrationForm, DeleteUserForm, SelectUserForm, 
    BetForm, ConfirmDeleteForm, ConfirmDeleteForm
)
import uuid
from app.blackjack import BlackjackGame

bp = Blueprint('main', __name__, static_folder='static')

def generate_session_id():
    return uuid.uuid4().hex[:4]  # генерируем 4 символа


@bp.route('/')
def index():
    if current_user.is_authenticated and not session.get('logged_out_once'):
        logout_user()
        session['logged_out_once'] = True
    if not current_user.is_authenticated:
        session.pop('logged_out_once', None)
    return redirect(url_for('main.index_page'))

@bp.route('/index', methods=['GET', 'POST'])
def index_page():
    form = SelectUserForm()
    delete_form = DeleteUserForm()
    return render_template('index.html', form=form, delete_form=delete_form)

@bp.route('/index2/<session_id>', methods=['GET'])
@login_required
def index2(session_id):
    if session_id != session.get('session_id'):
        flash("Invalid session ID")
        return redirect(url_for('main.index'))

    new_session_id = generate_session_id()
    session['session_id'] = new_session_id

    logout_form = DeleteUserForm()
    return render_template('index2.html', username=current_user.username, logout_form=logout_form, session_id=new_session_id)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.count() >= 10:
            flash('Max number of players reached')
            return redirect(url_for('main.register'))
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.password_hash = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('main.index_page'))
        except Exception as e:
            flash(f'Could not register user: {e}')
            db.session.rollback()
    else:
        if request.method == 'POST':
            flash('Form validation failed. See errors below.')
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        session_id = uuid.uuid4().hex[:4]  # генерируем 4 символа
        session['session_id'] = session_id
        return redirect(url_for('main.index2', session_id=session_id))
    form = LoginForm()
    if request.method == 'GET' and 'username' in request.args:
        form.username.data = request.args.get('username')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        session['logged_in_user'] = user.username

        session_id = uuid.uuid4().hex[:4]  # генерируем 4 символа
        session['session_id'] = session_id
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index2', session_id=session_id)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))

@bp.route('/confirm_delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def confirm_delete(user_id):
    form = ConfirmDeleteForm()
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        if form.confirm.data:
            db.session.delete(user)
            db.session.commit()
            flash(f'User {user.username} deleted successfully.')
            return redirect(url_for('main.index'))
        elif form.cancel.data:
            session_id = session.get('session_id')
            return redirect(url_for('main.index2', session_id=session_id))
    return render_template('confirm_delete.html', form=form, user=user, session_id=session.get('session_id'))

@bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if current_user.id == user.id:
                return redirect(url_for('main.confirm_delete', user_id=user.id))
            else:
                flash('You can only delete the logged-in user.')
        else:
            flash('User not found.')
    return redirect(url_for('main.index'))

@bp.route('/select_user', methods=['POST'])
def select_user():
    form = SelectUserForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            flash('Logout from the current user before selecting another one.')
            return redirect(url_for('main.index'))

        user = User.query.filter_by(id=form.user_id.data).first()
        if user:
            return redirect(url_for('main.login', username=user.username))
        else:
            flash('User not found.')
    return redirect(url_for('main.index'))

@bp.route('/start_game/<session_id>', methods=['GET', 'POST'])
@login_required
def start_game(session_id):
    if session_id != session.get('session_id'):
        flash("Invalid session ID")
        return redirect(url_for('main.index'))

    form = BetForm()

    if request.method == 'GET':
        return render_template('start_game.html', balance=current_user.balance, form=form, session_id=session_id)

    if form.validate_on_submit():
        bet = form.bet_amount.data
        try:
            current_user.place_bet(bet)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('main.start_game', session_id=session_id))

        # Инициализация игры
        game = BlackjackGame()
        game.start_new_game()
        game_state = game.get_game_state()
        new_game = Game(user_id=current_user.id, state=game_state)
        db.session.add(new_game)
        db.session.commit()

        # Сохранение данных игры в сессию
        session['game_id'] = new_game.id
        session['bet'] = bet

        new_session_id = generate_session_id()
        session['session_id'] = new_session_id

        return redirect(url_for('main.game', session_id=new_session_id))

    return render_template('start_game.html', title='Start Game', form=form, session_id=session_id)

@bp.route('/game/<session_id>', methods=['GET', 'POST'])
@login_required
def game(session_id):
    if session_id != session.get('session_id'):
        flash("Invalid session ID")
        return redirect(url_for('main.index'))

    game_id = session.get('game_id')
    bet = session.get('bet')
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for('main.start_game', session_id=session_id))

    if request.method == 'POST':
        if 'take_card' in request.form:
            try:
                blackjack_game = BlackjackGame(deck_id=game.state['deck_id'], player_hand=game.state['player_hand'], dealer_hand=game.state['dealer_hand'])
                card = blackjack_game.player_draw_card()
                game.state = blackjack_game.get_game_state()

                if blackjack_game.is_player_busted():
                    flash('You lose! Player is busted.')
                    game.state['game_over'] = True
                    game.state['game_message'] = 'You lose! Player is busted.'
                db.session.commit()

            except Exception as e:
                flash(str(e))
                return redirect(url_for('main.game', session_id=session_id))

        elif 'pass' in request.form:
            try:
                blackjack_game = BlackjackGame(deck_id=game.state['deck_id'], player_hand=game.state['player_hand'], dealer_hand=game.state['dealer_hand'])

                while blackjack_game.should_dealer_draw():
                    blackjack_game.dealer_draw_card()

                game.state = blackjack_game.get_game_state()

                dealer_busted = blackjack_game.is_dealer_busted()
                player_score = blackjack_game.get_player_score()
                dealer_score = blackjack_game.get_dealer_score()

                if dealer_busted or player_score > dealer_score:
                    flash('You win!')
                    current_user.receive_winnings(session['bet'] * 2)
                    game.state['game_message'] = 'You win!'
                else:
                    flash('You lose!')
                    game.state['game_message'] = 'You lose!'

                game.state['game_over'] = True
                db.session.commit()

            except Exception as e:
                flash(str(e))
                return redirect(url_for('main.game', session_id=session_id))

    game_state = game.state
    return render_template('game.html', state=game_state, bet=bet, session_id=session_id, username=current_user.username)

@bp.route('/pass', methods=['POST'])
@login_required
def pass_turn():
    game_id = session.get('game_id')
    game = Game.query.get(game_id)

    if game is None:
        return 'No active game', 400

    try:
        blackjack_game = BlackjackGame(deck_id=game.state['deck_id'], player_hand=game.state['player_hand'], dealer_hand=game.state['dealer_hand'])

        while blackjack_game.should_dealer_draw():
            blackjack_game.dealer_draw_card()

        game.state = blackjack_game.get_game_state()
        db.session.commit()

        dealer_busted = blackjack_game.is_dealer_busted()
        player_score = blackjack_game.get_player_score()
        dealer_score = blackjack_game.get_dealer_score()

        game_result = None
        if dealer_busted or player_score > dealer_score:
            game_result = 'player_wins'
            current_user.receive_winnings(session['bet'] * 2)
        else:
            game_result = 'player_loses'

        db.session.commit()

        return jsonify({
            'dealer_hand': blackjack_game.dealer_hand,
            'dealer_score': blackjack_game.get_dealer_score(),
            'game_over': True,
            'result': game_result
        })
    except Exception as e:
        return 'Error processing pass turn', 500