from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, validators
from .models import User
from .modules.models import Module

#If errors: check if adding 'validators.' before validators solves it...
class LoginForm(Form):
	username = StringField('username', [validators.InputRequired()])
	password = PasswordField('password', [validators.InputRequired()])
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = None

	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		user = User.query.filter_by(username=self.username.data).first()
		if user is None:
			self.username.errors.append('Unknown username')
			return False
		if(user.password != self.password.data):	
			self.password.errors.append('Invalid password')
			return False

		self.user = user
		return True

class SignupForm(Form):
	username = StringField('username', [validators.InputRequired()])
	email = StringField('email', [validators.InputRequired(), validators.Email(message='Must be an e-mail address')])
	password = PasswordField('password', [validators.InputRequired(), validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('confirm', [validators.InputRequired()])

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = None

	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		user = User.query.filter_by(username=self.username.data).first()
		if user is not None:
			self.username.errors.append('Username taken')
			return False

		return True

