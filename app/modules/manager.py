
import hashlib
import os
import os.path
import shutil
import subprocess
import sqlalchemy
import werkzeug

from app import app
from app import db
from app import util
from app.modules.models import Module, ModuleVersion
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound

class ModuleDuplicateVersionError(ValueError):
	'''Raise when a module already has a version with the same name.'''
class FileNotFoundError(ValueError):
	'''Raise when looked for file cannot be found.'''

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
	sys_path = 'app/static/img/default/modules/'
	web_path = '/static/img/default/modules/'
	
	from os import listdir
	from os.path import isfile, join
	onlyfiles = [f for f in listdir(sys_path) if isfile(join(sys_path, f)) and f != '.DS_Store']

	i    = sum(ord(c) for c in module_name) % len(onlyfiles)
	path = join(web_path, onlyfiles[i])
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

def exists_path_for_module_content(filename, module, version=None):
	if module is None:
		raise ValueError('Argument module must not be None')

	if filename == 'icon':
		# TODO: There is always a picture available for the module.
		# TODO: The semantics here could be changed to show whether 
		# 	these is a custom icon or not!
		return True
	
	if version is None:
		version = get_latest_ver_string(module.name)

	module_path = get_modver_sys_path(module_name=module.name, sVersion=version)
	sys_path    = os.path.join(module_path, filename)

	return os.path.exists(sys_path)


def get_path_for_module_content(filename, module, version=None):
	if module is None:
		raise ValueError('Argument module must not be None')

	if filename == 'icon':
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
	web_path    = os.path.join(module_path, filename)

	return web_path

def copy_version(target_version_path, source_version_path, exclude_list=[]):
	if source_version_path is None:
		return False

	ensure_module_path(target_version_path)
	for dirpath, dirnames, filenames in os.walk(source_version_path):
		for filename in filenames:
			src = os.path.join(source_version_path, filename)
			dst = os.path.join(target_version_path, filename)

			if src in exclude_list:
				continue

			shutil.copyfile(src, dst)
	return True

def persist_files_to_disk(target_path, added_files):
	ensure_module_path(target_path)

	for file in added_files:
		sFilename = werkzeug.utils.secure_filename(file.filename)
		path = os.path.join(target_path, sFilename)
		with open(path, 'wb+') as file_handle:
			file.save(file_handle)

import tempfile


## TODO: Persist files to temp folder, then reuse upload_version_path
def upload_version(module, sVersion, added_files, removed_file_paths=[]):
	with tempfile.TemporaryDirectory() as tmpdirname:
		persist_files_to_disk(tmpdirname, added_files)
		upload_version_path(module, sVersion, tmpdirname, removed_file_paths)
	return

def upload_version_path(module, version_name, added_files_root_path, removed_file_paths=[]):
	session = db.session

	try:
		prev_version      = module.get_latest_version().version_string
		prev_version_path = get_modver_sys_path(module.name, prev_version)
	except ModuleVersionNotFound:
		prev_version_path = None

	try:
		new_version = ModuleVersion(module_id=module.id, version_string=version_name)
		session.add(new_version)
		session.commit()

		module.latest_version = new_version.id
		session.add(module)

		curr_version      = module.get_latest_version().version_string
		curr_version_path = get_modver_sys_path(module.name, curr_version)

		session.commit()

		copy_version(curr_version_path, prev_version_path)
		copy_version(curr_version_path, added_files_root_path)

		update_module_desc(module)

	except sqlalchemy.exc.IntegrityError as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		# TODO: delete folder for version as well?
		raise ModuleDuplicateVersionError('Version {} already exists for module {}'.format(version_name, module.name))
	except Exception as e:
		session.rollback()
		db.session.delete(new_version)
		session.commit()
		# TODO: delete folder for version as well?
		raise e

	return

def delete_module(module):
	'''Delete a given module.
	Precondition: The database entry should already be removed.
	Postcondition: Best-effort removal of the underlying files.
	'''
	module_path = get_mod_sys_path(module.name)
	shutil.rmtree(module_path, ignore_errors=True)
	return

def update_module_desc(module):
	module_path = get_modver_sys_path(module.name)
	readme_path = module_path+'/README.md'

	if os.path.exists(readme_path):
		session = db.session

		html = readme_to_html(module)
		module.short_desc = util.get_first_html_paragraph(html)
		module.long_desc  = html
	
		session.add(module)
		session.commit()


def readme_to_html(module):
	'''Renders a README.md file to html using the github md renderer.
	'''
	module_path = get_modver_sys_path(module.name)
	readme_path = module_path+'/README.md'

	if os.path.exists(readme_path):
		res  = subprocess.run(['./external/markdown/gfm-md-to-html.rb', readme_path], stdout=subprocess.PIPE)
		html_as_bytes = res.stdout
		return html_as_bytes.decode('utf-8')

	raise FileNotFoundError()