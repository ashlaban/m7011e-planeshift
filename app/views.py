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
 
# TODO: Implement salted passwords: http://flask.pocoo.org/snippets/54/
@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		########################################################################################
		#Confirmation and error handling implemented in login form. Much cleaner!
		login_user(form.user)
		flash('Successfully logged in as %s' % form.user.username)
		return redirect(url_for('index'))
		
	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, password=form.password.data, email=form.email.data)
		db.session.add(user)
		db.session.commit()
		flash('Thanks for signing up')
		return redirect(url_for('login'))

	return render_template('signup.html', title='Signup', form=form)

@app.route('/api/login', methods=['POST'])
def api_login():
	print(request)
	args = util.parse_request_to_json(request)

	username = werkzeug.utils.escape(args['username'])
	password = args['password']

	if not User.authenticate(username, password):
		return util.make_json_error(msg='Authentication failed.')
	
	user = User.get_by_name(username)
	login_user(user)
	return util.make_json_success(msg='Logged in successfully.')
		
	
