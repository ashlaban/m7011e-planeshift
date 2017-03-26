
from app import db

from werkzeug.security import generate_password_hash, check_password_hash

class UserNotFoundError(ValueError):
	'''Raise if a specific user cannot be found in db.'''

class User(db.Model):
	id       = db.Column(db.Integer     , primary_key=True)
	username = db.Column(db.String(64)  , index=True, unique=True)
	password = db.Column(db.String(160) , unique=False)
	email    = db.Column(db.String(120) , unique=True)

	@staticmethod
	def get_by_id(id):
		user = User.query.filter_by(id=id).first()
		if user is None:
			raise UserNotFoundError()
		return user

	@staticmethod
	def get_by_name(name):
		user = User.query.filter_by(username=name).first()
		if user is None:
			raise UserNotFoundError()
		return user

	@staticmethod
	def get_by_email(email):
		user = User.query.filter_by(email=email).first()
		if user is None:
			raise UserNotFoundError()
		return user

	@staticmethod
	def authenticate(name, password):
		try:
			user = User.get_by_name(name)
		except UserNotFoundError:
			return False
		is_validated = check_password_hash(user.password, password)
		return is_validated

	@staticmethod
	def exists(name):
		try:
			user = User.get_by_name(name)
		except UserNotFoundError:
			return False
		return True

	def exists_email(email):
		try:
			user = User.get_by_email(email)
		except UserNotFoundError:
			return False
		return True

	def __init__(self, password, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.set_password(password)

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(password, self.password)

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)
	
	def __repr__(self):
		return '<User %r>' % (self.username)

	def get_public_data(self):
		return {
			'username': self.username,
			'email'   : self.email,
		}

