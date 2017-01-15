from app import db
from app.modules.models import Module
from app.models import User

class Plane(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	#uuid = db.Column(db.String(64), index=True, unique=True)
	owner = db.Column(db.Integer, db.ForeignKey('user.id'))
	password = db.Column(db.String(64), index=True, nullable=True, unique=False)
	module = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)
	data = db.Column(db.LargeBinary, nullable=True, unique=False)
	name = db.Column(db.String(64), index=True, unique=False)
	public = db.Column(db.Boolean, index=True, unique=False)
		
	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	'''
	def get_uuid(self):
		return str(self.uuid)
	'''

	def get_owner(self):
		return User.query.get(int(self.owner))

	def get_module(self):
		module = Module.query.get(int(self.module))
		return module

	def get_name(self):
		return str(self.name)

	def is_public(self):
		if int(self.public):
			return True
		return False

	def has_password(self):
		if self.password is not None:
			return True
		return False

	@staticmethod
	def get_planes():
		return Plane.query.all()

	@staticmethod
	def get_plane(name):
		return Plane.query.filter_by(name=name).first()
	
	def __repr__(self):
		return '<Name %r>' % (self.name)

class Session(db.Model):
	user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	plane = db.Column(db.Integer, db.ForeignKey('plane.id'), primary_key=True)

	def get_user(self):
		return User.query.get(int(self.user))

	def get_plane(self):
		return Plane.query.get(int(self.plane))

	@staticmethod
	def get_sessions():
		return Session.query.all()

	@staticmethod
	def get_sessions(user):
		return Session.query.filter_by(user=user.id).all()

	@staticmethod
	def get_users_for_plane(plane):
		return Session.query.filter_by(plane=plane.id).all()

	@staticmethod
	def get_session(user, plane):
		return Session.query.filter_by(user=user.id, plane=plane.id).first()
