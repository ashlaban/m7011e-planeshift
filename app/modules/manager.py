
import os
import sqlalchemy

from app import app
from app import db
from app.modules.models import Module, ModuleVersions

# TODO: Convert this to singleton object? Or are these package objects akin to python singletons?

class ModuleDuplicateVersionError(Exception): pass

def get_file_basename(module_name, escaped_version):
	filebasename = '{}-{}'.format(module_name, escaped_version)
	return filebasename

def get_module_path(module_name, escaped_version):
	module_path  = os.path.join(module_name, escaped_version)
	full_path    = os.path.join( app.config['STATIC_UPLOAD_FOLDER'], module_path)

	return full_path

def get_module_system_path(module_name, escaped_version):
	module_path  = os.path.join(module_name, escaped_version)
	full_path    = os.path.join( app.config['UPLOAD_FOLDER'], module_path)

	return full_path

def ensure_module_path(module_name, escaped_version):
	module_path = get_module_path(module_name, escaped_version)
	return os.makedirs(module_path, exist_ok=True)

def get_path_for_module_content(ext, module_name, escaped_version=None):
	ALLOWED_FILE_TYPES = ['html', 'css', 'js']

	if ext not in ALLOWED_FILE_TYPES:
		raise ValueError('Argument ext ({}) not in ALLOWED_FILE_TYPES ({})'.format(ext, ALLOWED_FILE_TYPES))

	if escaped_version is None:
		module          = Module.get_by_name(module_name)
		escaped_version = module.get_escaped_version()

	module_path = get_module_path(module_name=module_name, escaped_version=escaped_version)
	basename    = get_file_basename(module_name=module_name, escaped_version=escaped_version)
	filename    = '{basename}.{ext}'.format(basename=basename, ext=ext)

	return os.path.join(module_path, filename)

def upload_version(module, escaped_version, files_dict):
	# TODO: The from argument should be extracted 
	# session = db.create_session(options={})
	session = db.session
	try:
		new_version = ModuleVersions(module_id=module.id, version_string=escaped_version)
		session.add(new_version)
		session.commit()

		module.latest_version = new_version.id
		session.add(module)

		module_path = get_module_system_path(module_name=module.name, escaped_version=escaped_version)
		ensure_module_path(module.name, escaped_version)

		filebasename = get_file_basename(module_name=module.name, escaped_version=escaped_version)

		html_filename = os.path.join(module_path, '{}.{}'.format(filebasename, 'html'))
		css_filename  = os.path.join(module_path, '{}.{}'.format(filebasename, 'css' ))
		js_filename   = os.path.join(module_path, '{}.{}'.format(filebasename, 'js'  ))

		with open(html_filename, 'wb+') as html_file:
			html_file.write(files_dict['html'])
		with open(css_filename, 'wb+') as css_file:
			css_file.write(files_dict['css'])
		with open(js_filename, 'wb+') as js_file:
			js_file.write(files_dict['js'])

		session.commit()

	except sqlalchemy.exc.IntegrityError:
		session.rollback()
		raise ModuleDuplicateVersionError('Version {} already exists for module {}'.format(escaped_version, module.name))

	return



