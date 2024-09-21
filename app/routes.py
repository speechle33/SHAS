from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Game
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from app.forms import (
    LoginForm, RegistrationForm, DeleteUserForm, SelectUserForm, 
    BetForm, ConfirmDeleteForm, ConfirmDeleteForm
)


bp = Blueprint('main', __name__)

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

@bp.route('/index2/<username>', methods=['GET'])
@login_required
def index2(username):
    if username != current_user.username:
        flash("You are not authorized to view this page")
        return redirect(url_for('main.index'))

    logout_form = DeleteUserForm()
    return render_template('index2.html', username=username, logout_form=logout_form)

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
        return redirect(url_for('main.index2', username=current_user.username))
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
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index2', username=user.username)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    session.pop('logged_in_user', None)
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
            return redirect(url_for('main.index2', username=current_user.username))
    return render_template('confirm_delete.html', form=form, user=user)

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
            # Имя пользователя передается через параметр
            return redirect(url_for('main.login', username=user.username))
        else:
            flash('User not found.')
    return redirect(url_for('main.index'))

@bp.route('/start_game/<int:player_id>', methods=['GET', 'POST'])
@login_required
def start_game(player_id):
    form = BetForm()
    if form.validate_on_submit():
        bet = form.bet_amount.data
        try:
            current_user.place_bet(bet)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('main.start_game', player_id=player_id))

        from app.blackjack import BlackjackGame
        game = BlackjackGame()
        game_state = game.get_game_state()
        new_game = Game(user_id=player_id, state=game_state)
        db.session.add(new_game)
        db.session.commit()

        session['game_id'] = new_game.id
        session['bet'] = bet
        return redirect(url_for('main.game'))
    return render_template('start_game.html', title='Start Game', form=form)

@bp.route('/game')
@login_required
def game():
    game_id = session.get('game_id')
    bet = session.get('bet')
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for('main.start_game', player_id=current_user.id))
    game_state = game.state
    return render_template('game.html', state=game_state, bet=bet)

@bp.route('/hit', methods=['POST'])
@login_required
def hit():
    game_id = session.get('game_id')
    game = Game.query.get(game_id)
    if game:
        from app.blackjack import BlackjackGame
        blackjack_game = BlackjackGame()
        blackjack_game.deck = game.state['deck']
        blackjack_game.player_hand = game.state['player_hand']
        blackjack_game.dealer_hand = game.state['dealer_hand']
        blackjack_game.hit(blackjack_game.player_hand)

        game_state = blackjack_game.get_game_state()
        game.state = game_state
        db.session.commit()

        result = blackjack_game.is_over()
        if result:
            handle_game_over(result)

        return jsonify(game_state)
    return 'No active game', 400

@bp.route('/stand', methods=['POST'])
@login_required
def stand():
    game_id = session.get('game_id')
    game = Game.query.get(game_id)
    if game:
        from app.blackjack import BlackjackGame
        blackjack_game = BlackjackGame()
        blackjack_game.deck = game.state['deck']
        blackjack_game.player_hand = game.state['player_hand']
        blackjack_game.dealer_hand = game.state['dealer_hand']

        while blackjack_game.calculate_score(blackjack_game.dealer_hand) < 17:
            blackjack_game.hit(blackjack_game.dealer_hand)

        game_state = blackjack_game.get_game_state()
        game.state = game_state
        db.session.commit()

        result = blackjack_game.is_over()
        if result:
            handle_game_over(result)

        return jsonify(game_state)
    return 'No active game', 400

def handle_game_over(result):
    bet = session.get('bet')
    game_id = session.get('game_id')
    game = Game.query.get(game_id)
    from app.blackjack import BlackjackGame
    blackjack_game = BlackjackGame()
    blackjack_game.deck = game.state['deck']
    blackjack_game.player_hand = game.state['player_hand']
    blackjack_game.dealer_hand = game.state['dealer_hand']

    if result == 'player_bust' or blackjack_game.calculate_score(blackjack_game.player_hand) < blackjack_game.calculate_score(blackjack_game.dealer_hand):
        current_user.balance -= bet
    else:
        current_user.balance += bet * 2

    db.session.commit()

@bp.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.balance.desc()).all()
    return render_template('leaderboard.html', users=users)