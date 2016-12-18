# Import flask dependencies
from flask import Blueprint, render_template, redirect, flash, url_for, g, request
#, request, flash, g, session, url_for

from app import app

from app import db, util
from app.modules.models import Module
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound
from app.modules.forms  import UploadForm, VersionForm
from app.modules import manager

from app import util

import sqlalchemy
import collections
import werkzeug
import pathlib

# Define blueprints
modules    = Blueprint('modules_mod', __name__, url_prefix='/modules')
module_api = Blueprint('modules_api', __name__, url_prefix='/api/modules')

# =============================================================================
# Frontend endpoints
# =============================================================================
@modules.route('/')
def list_module():
	modules = db.session.query(Module)
	return render_template('modules/index.html', modules=modules)

@modules.route('/create')
def create_module():
	render_template('modules/create.html')

# TODO: Should be protected. Only logged in owners should be able to modify.
# NOTE: Stored filename will become modulename-versionstring.xxx
@modules.route('/upload/<name>', methods=['GET', 'POST'])
def upload_module(name):
	if not g.user.is_authenticated:
		return redirect(url_for('login'))

	if not g.user.id == module.owner:
		return render_template('modules/403.html', name=name)

	module = Module.get_by_name(name)

	form = UploadForm()
	if form.validate_on_submit():
		try:
			escaped_version = werkzeug.utils.escape(form.version.data)
			files_dict      = form.get_files_dict()
			manager.upload_version(module=module, escaped_version=escaped_version, files_dict=files_dict)

			flash('Version {} uploaded successfully!'.format(escaped_version), 'message')
			return redirect( url_for('modules.info_module', name=name) )

		except manager.ModuleDuplicateVersionError:
			flash('Version {} already exists.'.format(escaped_version), 'error')

	return render_template('modules/upload.html', module_name=name, form=form)


@modules.route('/name/<name>')
def info_module(name):
	module   = Module.get_by_name(name)
	versions = Module.get_versions_for_module_id(module.id)
	versions = [(v.id, v.version_string) for v in versions]

	is_owner = g.user.is_authenticated and g.user.id == module.owner

	form = VersionForm(versions)
	if form.validate_on_submit():
		pass
	
	if module is None:
		return render_template('modules/404.html', name=name)

	return render_template('modules/module.html', module=module, form=form, is_owner=is_owner)

# =============================================================================
# API endpoints
# NOTE: If a resource is created, the correct response code should be returned
# 	201 - Create
# NOTE: Location reference should be to the newly created resource
# [x] Post to /api/modules -> Create/update module
# [x] Get to /api/modules -> list all modules
# [/] DELETE to /api/modules -> Delete module
# [x] Get to /api/modules/NewModule -> get info about module
# [/] Post to /api/modules/NewModule -> create/update verison
# [x] /api/modules/NewModule/latest -> Symlink to /xyz that is the latest version.
# [o] Get to /api/modules/NewModule/<version> -> Info specific to that version
# [o] Post to /api/modules/NewModule/<version> -> Create new version
# [x] Get to /api/modules/NewModule/<version>/<file> -> Get path for that resource
# [/] Post to /api/modules/NewModule/<version>/<file> -> Update/Create that resouce
#
# TODO: It would be possible to cache common queries for a short 
# while to reduce load on cpu while maintaining quick updates
# 
# =============================================================================
@module_api.route('/', methods=['GET'])
def api_list():
	'''List all modules in database.
	'''
	try:
		modules = Module.query
	except Exception:
		return util.make_json_error()

	data = [ module.get_public_short_info() for module in modules ]

	return util.make_json_success(data=data)

@module_api.route('/', methods=['POST'])
def api_module():
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
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	module_name = html_escape_or_none(args['name'])
	short_desc  = html_escape_or_none(args['short_desc'])
	long_desc   = html_escape_or_none(args['long_desc'])

	picture        = args['picture']
	latest_version = None

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		module = Module(
			owner = g.user.id,
			name  = module_name,
			short_desc = short_desc,
			long_desc  = long_desc,

			picture        = picture,
			latest_version = latest_version,
		)

	if short_desc is not None:
		module.short_desc = short_desc
	if long_desc is not None:
		module.long_desc = long_desc
	if picture is not None:
		module.picture = picture

	db.session.add(module)

	try:
		db.session.commit()
	except sqlalchemy.exc.IntegrityError as e:
		return util.make_json_error(msg='Invalid arguments.')

	return util.make_json_success(msg='Module created.')

@module_api.route('/', methods=['DELETE'])
def api_delete():
	'''Delete a module. Requires user to be authenticated and the owner to 
	complete successfully.
	
	Arguments
		name - String - Required. Deletes the module with the given name.

	Returns
		{status: ok} if operation successful.
		{status: error, msg: '...'} otherwise.
	'''
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')
	
	args = util.parse_request_to_json(request)
	name = html_escape_or_none(args['name'])

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	if g.user.id != module.owner:
		return util.make_json_error(msg='You do not own module {}.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/<module_name>', methods=['GET'])
def api_info(name):
	'''Get meta-data for a given module.
	'''
	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found'.format(name))

	data = module.get_public_long_info()
	return util.make_json_success(data=data)

@module_api.route('/<module_name>', methods=['POST'])
def api_version(module_name):
	'''Create a new version. Must be authenticated as owner.
	Arguemnts
		name - String - Required. Name of the new version.

	Returns
		{status: ok} if successful
		{status: error, msg: '...'} if user not authenticated or not owner.
	'''
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	try:
		module = Module.get_by_name(module_name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	if not module.is_owner(g.user):
		return util.make_json_error(msg='You do not have the correct permissions.')

	args = util.parse_request_to_json(request)
	name = html_escape_or_none(args['name'])

	return util.make_json_error(msg='Not implemented yet')

# @module_api.route('/<module_name>/<version>', methods=['GET'])
# def api_version_get(module_name, version):
# 	return util.make_json_error(msg='Not implemented yet')

# @module_api.route('/<module_name>/<version>', methods=['POST'])
# def api_version_post(module_name, version):
# 	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/<module_name>/<version>/<file>' methods=['GET'])
def api_content_path_get(module_name, version, file):
	if version == 'latest':
		version = None

	try:
		module         = Module.get_by_name(module_name)
		module_version = module.get_version(version) if version is not None else None

		if file in ['html', 'css', 'js', 'pic']:
			data = manager.get_path_for_module_content(file, module, module_version)
		else:
			return make_json_error(msg='File {} not found.'.format(file))
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))
	except ModuleVersionNotFound:
		return util.make_json_error(msg='Version {} not found for module {}'.format(version, module_name))
	except ModuleHasNoData:
		return util.make_json_error(msg='No version uploaded for module {} yet!'.format(module_name))
	
	return util.make_json_success(data=data)

@module_api.route('/<module_name>/<version>/<file>', methods=['POST'])
def api_content_path_post(name, version, file):
	if version == 'latest':
		version = None

	try:
		module         = Module.get_by_name(module_name)
		module_version = module.get_version(version) if version is not None else None

		# TODO: Implement upload here.

	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))
	except ModuleVersionNotFound:
		return util.make_json_error(msg='Version {} not found for module {}'.format(version, module_name))
	except ModuleHasNoData:
		return util.make_json_error(msg='No version uploaded for module {} yet!'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')	
