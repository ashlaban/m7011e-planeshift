from flask_wtf      import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, validators

class VersionForm(Form):
	version_list = SelectField('version', coerce=int);

	def __init__(self, version_list_data, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

		self.version_list.choices = version_list_data

class UploadForm(Form):
	version = StringField('version', [validators.InputRequired()])
	html = FileField('html', validators=[FileRequired(), FileAllowed(['html'], 'HTML only!')])
	css  = FileField('css' , validators=[FileRequired(), FileAllowed(['css' ], 'CSS only!')])
	js   = FileField('js'  , validators=[FileRequired(), FileAllowed(['js'  ], 'JS only!')])
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		return True

	def get_files_dict(self):
		files_dict = {
			'html': self.html.data.read() if self.html.data else None,
			'css' : self.css.data.read()  if self.css.data  else None,
			'js'  : self.js.data.read()   if self.js.data   else None,
		}
		
		return files_dict