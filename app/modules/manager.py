
import os
import sqlalchemy

from app import app
from app import db
from app.modules.models import Module, ModuleVersion
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound

class ModuleDuplicateVersionError(ValueError):
	'''Raise when a module already has a version with the same name.'''

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
	module_path = get_module_system_path(module_name, escaped_version)
	return os.makedirs(module_path, exist_ok=True)

def get_path_for_module_content(ext, module, version=None):
	ALLOWED_FILE_TYPES = ['html', 'css', 'js', 'pic']

	if ext not in ALLOWED_FILE_TYPES:
		raise ValueError('Argument ext ({}) not in ALLOWED_FILE_TYPES ({})'.format(ext, ALLOWED_FILE_TYPES))

	if version is None:
		try:
			version        = module.get_latest_version()
			version_string = version.get_escaped_version_string()
		except ModuleVersionNotFound:
			raise ModuleHasNoData()

	module_path = get_module_path(module_name=module_name, escaped_version=escaped_version)
	basename    = get_file_basename(module_name=module_name, escaped_version=escaped_version)
	filename    = '{basename}.{ext}'.format(basename=basename, ext=ext)

	return os.path.join(module_path, filename)

def upload_file_helper(filetype, data, module_name, escaped_version):	
	if data:
		target_path = get_module_system_path(module_name=module_name, escaped_version=escaped_version)
		ensure_module_path(module_name, escaped_version)

		filebasename = get_file_basename(module_name=module_name, escaped_version=escaped_version)
		filename     = os.path.join(target_path, '{}.{}'.format(filebasename, filetype))
		with open(filename, 'wb+') as file:
			file.write(data)

def upload_version(module, escaped_version, files_dict):
	# TODO: The from argument should be extracted
	# session = db.create_session(options={})
	session = db.session
	try:
		new_version = ModuleVersion(module_id=module.id, version_string=escaped_version)
		session.add(new_version)
		session.commit()

		module.latest_version = new_version.id
		session.add(module)

		upload_file_helper('html', files_dict['html'], module.name, escaped_version)
		upload_file_helper('css' , files_dict['css'] , module.name, escaped_version)
		upload_file_helper('js'  , files_dict['js']  , module.name, escaped_version)

		session.commit()

	except sqlalchemy.exc.IntegrityError:
		session.rollback()
		raise ModuleDuplicateVersionError('Version {} already exists for module {}'.format(escaped_version, module.name))

	return



