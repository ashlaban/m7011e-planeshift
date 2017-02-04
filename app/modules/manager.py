
import os
import sqlalchemy

from app import app
from app import db
from app.modules.models import Module, ModuleVersion
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound

import werkzeug

class ModuleDuplicateVersionError(ValueError):
	'''Raise when a module already has a version with the same name.'''

def get_file_basename(module_name, sVersion):
	filebasename = '{}-{}'.format(module_name, sVersion)
	return filebasename

def get_module_path(module_name, sVersion):
	module_path  = os.path.join(module_name, sVersion)
	full_path    = os.path.join( app.config['STATIC_UPLOAD_FOLDER'], module_path)

	return full_path

def get_module_system_path(module_name, sVersion):
	module_path  = os.path.join(module_name, sVersion)
	full_path    = os.path.join( app.config['UPLOAD_FOLDER'], module_path)

	return full_path

def ensure_module_path(module_name, sVersion):
	module_path = get_module_system_path(module_name, sVersion)
	return os.makedirs(module_path, exist_ok=True)

def get_path_for_module_content(filename, module, version=None):
	if module is None:
		raise ValueError('Argument module must not be None')

	if version is None:
		try:
			version        = module.get_latest_version()
			version_string = version.get_escaped_version()
		except ModuleVersionNotFound:
			raise ModuleHasNoData()

	module_path = get_module_path(module_name=module.name, sVersion=version_string)
	return os.path.join(module_path, filename)

def upload_file_helper(file, module_name, sVersion):
	target_path = get_module_system_path(module_name=module_name, sVersion=sVersion)
	ensure_module_path(module_name, sVersion)

	sFilename = werkzeug.utils.secure_filename(file.filename)
	path = os.path.join(target_path, sFilename)
	with open(path, 'wb+') as file_handle:
		file.save(file_handle)

def upload_version(module, sVersion, files):
	session = db.session
	try:
		new_version = ModuleVersion(module_id=module.id, version_string=sVersion)
		session.add(new_version)
		session.commit()

		module.latest_version = new_version.id
		session.add(module)

		for file in files:
			upload_file_helper(file, module.name, sVersion)

		session.commit()

	except sqlalchemy.exc.IntegrityError as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		raise ModuleDuplicateVersionError('Version {} already exists for module {}'.format(sVersion, module.name))
	except Exception as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		raise e

	return



