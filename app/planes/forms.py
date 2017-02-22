from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, validators
from app.planes.models import Plane
from app.modules.models import Module

class PlaneCreateForm(Form):
	name     = StringField('name', [validators.InputRequired()])
	password = PasswordField('password')
	# module   = SelectField('module', coerce=str)
	# version  = SelectField('version', coerce=int)
	hidden   = BooleanField('hidden', default=False)

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	# def get_modules(self):
	# 	modules = []
	# 	for m in Module.query.all():
	# 		if m.has_version():
	# 			modules.append((m.name, m.name))
	# 	return modules

class PlanarAuthenticateForm(Form):
	password = PasswordField('password')

	def __init__(self, plane_name, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.plane_name = plane_name
		self.plane = None

	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		plane = Plane.query.filter_by(name=self.plane_name).first()
		if(plane.password != self.password.data):	
			self.password.errors.append('Invalid password')
			return False

		self.plane = plane
		return True
