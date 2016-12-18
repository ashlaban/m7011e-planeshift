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
	
	def __repr__(self):
		return '<Name %r>' % (self.name)
