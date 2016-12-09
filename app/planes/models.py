
from app import db

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
