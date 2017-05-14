from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden
from flask_login import login_user, logout_user
from .. import db
from ..email import send_email

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})


@api.route('/login/', methods = ['POST'])
def user_login():
    email = request.form['email']
    psw = request.form['psw']
    # email = request.json.get('email')
    # psw = request.json.get('psw')
    user = User.query.filter_by(email = email).first()
    if user is not None and user.verify_password(psw):
        login_user(user, True)
        return jsonify({'user': user.to_json(),
                         'token': user.generate_auth_token()})

@api.route('/logout/', methods = ['POST'])
def user_logout():
    email = request.form['email']
    # email = request.json.get('email')
    # psw = request.json.get('psw')
    user = User.query.filter_by(email = email).first()
    if user:
        logout_user(user)
        return jsonify({'user': user.to_json()})

@api.route('/register/', methods = ['POST'])
def user_register():
    email = request.form['email']
    psw = request.form['psw']
    username = request.form['username']
    # email = request.json.get('email')
    # psw = request.json.get('psw')
    # username = request.json.get('username')
    user = User(email=email, password=psw, username=username)
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    send_email(user.email, 'Confirm Your Account',
               'auth/email/confirm', user = user, token = token)
    return jsonify({'user': user.to_json()})
