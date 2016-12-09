from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, validators
from app.planes.models import Plane
from app.modules.models import Module

class CreatePlaneForm(Form):
	name = StringField('name', [validators.InputRequired()])
	password = PasswordField('password')
	module = SelectField('module', coerce=int)
	public = BooleanField('public', default=False)

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def getModules(self):
		#modules = Module.query(Module.name).all()
		modules = []
		for m in Module.query.all():
			modules.append((m.id, m.name))
		return modules

	'''
	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		return True
	'''
