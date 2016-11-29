from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm
from .models import User

#Not currently used, I think...
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

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		#Queries all users. Find a way to only query correct username!
		users = User.query.all()
		for u in users:
			if(u.username==form.username.data and u.password==form.password.data):
				login_user(u)
				flash('User %s successfully logged in.' % (u.username))
				return redirect(url_for('index'))
				
		flash('Wrong username or password!')
		return redirect(url_for('login'))
	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
