from flask_wtf      import Form
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import TextAreaField, FileField, StringField, validators

class UploadForm(Form):
	version = StringField('version', [validators.InputRequired()])
	html = FileField('html', validators=[FileAllowed(['html'], 'The HTML field takes HTML files only.')])
	css  = FileField('css' , validators=[FileAllowed(['css' ], 'The CSS field takes CSS files only.')])
	js   = FileField('js'  , validators=[FileRequired(), FileAllowed(['js'], 'The JS field takes JS files only.')])
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def get_files_dict(self):
		files_dict = {
			'html': self.html.data.read() if self.html.data else None,
			'css' : self.css.data.read()  if self.css.data  else None,
			'js'  : self.js.data.read()   if self.js.data   else None,
		}
		
		return files_dict

class CreateForm(Form):
	'''Create a module.
	Arguments
		module_name - String - Required. Name of module. If module does not 
		                       exist it will be created.
		short_desc  - String - Short description of module. Will be included in
		                       listings.
		long_desc   - String - Longer description of module. Will not be 
		                       included in listings.
		picture     - String base64 - Icon to represent the module.
	'''
	name       = StringField('name', [validators.InputRequired()])
	short_desc = TextAreaField('short_desc', [validators.InputRequired()])
	long_desc  = TextAreaField('long_desc')
	picture    = TextAreaField('picture')
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False
		# TODO: Custom validation.
		return True

