from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, SignupForm
from .models import User
from .modules.models import Module

from app import util
from app.models import UserNotFoundError

import collections
import werkzeug
import sqlalchemy

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home')
 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	return render_template('signup.html', title='Signup', form=form)

# TODO: Implement salted passwords: http://flask.pocoo.org/snippets/54/
@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
# @login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/api/signup', methods=['POST'])
def api_signup():
	args = util.parse_request_to_json(request)
	form = SignupForm.from_json(args, csrf_enabled=False)
	# username = werkzeug.utils.escape(args['username'])
	# password = werkzeug.utils.escape(args['password'])
	# email    = werkzeug.utils.escape(args['email'])

	if not form.validate():
		return util.make_json_error(msg='Malformed data.')
	
	user = User(username=form.username.data, password=form.password.data, email=form.email.data)
	db.session.add(user)
	db.session.commit()

	login_user(user)
	return util.make_json_success(msg='Thanks for signing up.')

@app.route('/api/login', methods=['POST'])
def api_login():
	# username = werkzeug.utils.escape(args['username'])
	# password = werkzeug.utils.escape(args['password'])

	# if not User.authenticate(username, password):
	# 	return util.make_json_error(msg='Authentication failed.')
	
	args = util.parse_request_to_json(request)
	form = LoginForm.from_json(args, csrf_enabled=False)

	if not form.validate():
		return util.make_json_error(msg='Malformed data.')
	
	user = User.get_by_name(form.username.data)
	login_user(user)
	return util.make_json_success(msg='Welcome.')
		
	
