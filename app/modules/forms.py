from flask_wtf      import Form
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import TextAreaField, FileField, StringField, validators

class CreateForm(Form):
	'''Create a module.
	Arguments
		module_name - String - Required. Name of module. If module does not 
		                       exist it will be created.
		short_desc  - String - Short description of module. Will be included in
		                       listings.
		long_desc   - String - Longer description of module. Will not be 
		                       included in listings.
	'''
	name       = StringField('name', [validators.InputRequired()])
	short_desc = TextAreaField('short_desc', [validators.InputRequired()])
	long_desc  = TextAreaField('long_desc')
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False
		# TODO: Custom validation.
		return True

