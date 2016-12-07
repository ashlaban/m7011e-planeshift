
from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password = db.Column(db.String(64), index=True, unique=False)
	email = db.Column(db.String(120), index=True, unique=True)

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
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)
	
	def __repr__(self):
		return '<User %r>' % (self.username)

class Plane(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	owner = db.Column(db.Integer, db.ForeignKey('user.id'))
	password = db.Column(db.String(64), index=True, nullable=True, unique=False)
	module = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)
	data = db.Column(db.LargeBinary, index=True, nullable=True, unique=False)
	name = db.Column(db.String(64), index=True, unique=False)
	public = db.Column(db.Boolean, index=True, unique=False)
		
	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)
	
	def __repr__(self):
		return '<Name %r>' % (self.name)
