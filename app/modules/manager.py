
import os
import sqlalchemy

from app import app
from app import db
from app.modules.models import Module, ModuleVersion
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound

import shutil
import os
import os.path

import werkzeug
import hashlib

class ModuleDuplicateVersionError(ValueError):
	'''Raise when a module already has a version with the same name.'''

def get_file_basename(module_name, sVersion):
	filebasename = '{}-{}'.format(module_name, sVersion)
	return filebasename

def get_latest_ver_string(module_name):
	try:
		module   = Module.get_by_name(module_name)
		version  = module.get_latest_version()
		sVersion = version.get_escaped_version()
	except ModuleVersionNotFound:
		raise ModuleHasNoData()
	return sVersion

def get_default_icon_path(module_name):
	num_files = 4
	i    = sum(ord(c) for c in module_name) % num_files
	path = '/static/img/default/modules/{}.png'.format(i)
	return path

def get_mod_web_path(module_name):
	return os.path.join( app.config['WEB_UPLOAD_FOLDER'], module_name)

def get_mod_sys_path(module_name):
	return os.path.join( app.config['SYS_UPLOAD_FOLDER'], module_name)
	
def get_modver_web_path(module_name, sVersion=None):
	if sVersion is None:
		sVersion = get_latest_ver_string(module_name)

	module_path  = get_mod_web_path(module_name)
	full_path    = os.path.join(module_path, sVersion)
	return full_path

def get_modver_sys_path(module_name, sVersion=None):
	if sVersion is None:
		sVersion = get_latest_ver_string(module_name)

	module_path  = get_mod_sys_path(module_name)
	full_path    = os.path.join(module_path, sVersion)
	return full_path

def ensure_module_path(path):
	return os.makedirs(path, exist_ok=True)

def get_path_for_module_content(filename, module, version=None):
	if module is None:
		raise ValueError('Argument module must not be None')

	if filename == 'icon.png':
		try:
			module_sys_path = get_modver_sys_path(module_name=module.name, sVersion=version)
			full_sys_path   = os.path.join(module_sys_path, filename)
			if not os.path.isfile(full_sys_path):
				return get_default_icon_path(module.name)
		except:
			return get_default_icon_path(module.name) 
	
	if version is None:
		version = get_latest_ver_string(module.name)

	module_path = get_modver_web_path(module_name=module.name, sVersion=version)
	return os.path.join(module_path, filename)

def copy_prev_version(curr_version_path, prev_version_path, exclude_list=[]):
	if prev_version_path is None:
		return False

	ensure_module_path(curr_version_path)
	for dirpath, dirnames, filenames in os.walk(prev_version_path):
		for filename in filenames:
			src = os.path.join(prev_version_path, filename)
			dst = os.path.join(curr_version_path, filename)

			if src in exclude_list:
				continue

			shutil.copyfile(src, dst)
	return True

def persist_files_to_disk(target_path, added_files, removed_file_paths):
	ensure_module_path(target_path)

	for file in added_files:
		sFilename = werkzeug.utils.secure_filename(file.filename)
		path = os.path.join(target_path, sFilename)
		with open(path, 'wb+') as file_handle:
			file.save(file_handle)

def upload_version(module, sVersion, added_files, removed_file_paths=[]):
	session = db.session

	try:
		prev_version      = module.get_latest_version().version_string
		prev_version_path = get_modver_sys_path(module.name, prev_version)
	except ModuleVersionNotFound:
		prev_version_path = None

	try:
		new_version = ModuleVersion(module_id=module.id, version_string=sVersion)
		session.add(new_version)
		session.commit()

		module.latest_version = new_version.id
		session.add(module)

		curr_version      = module.get_latest_version().version_string
		curr_version_path = get_modver_sys_path(module.name, curr_version)

		session.commit()

		copy_prev_version(curr_version_path, prev_version_path)
		persist_files_to_disk(curr_version_path, added_files, removed_file_paths)

	except sqlalchemy.exc.IntegrityError as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		# TODO: delete folder for version as well?
		raise ModuleDuplicateVersionError('Version {} already exists for module {}'.format(sVersion, module.name))
	except Exception as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		# TODO: delete folder for version as well?
		raise e

	return

def delete_module(module):
	"""Delete a given module.
	Precondition: The database entry should already be removed.
	Postcondition: Best-effort removal of the underlying files.
	"""
	module_path = get_mod_sys_path(module.name)
	shutil.rmtree(module_path, ignore_errors=True)
	return
