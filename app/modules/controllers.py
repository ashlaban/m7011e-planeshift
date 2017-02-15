# Import flask dependencies
from flask import Blueprint, render_template, redirect, flash, url_for, g, request
#, request, flash, g, session, url_for

from app import app

from app import db, util
from app.modules.models import Module
from app.modules.models import ModuleNotFound, ModuleHasNoData, ModuleVersionNotFound
from app.modules.forms  import CreateForm
from app.modules import manager

from app.models import User
from app.models import UserNotFoundError

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
	if not g.user.is_authenticated:
		return render_template('/403.html')

	form = CreateForm()
	return render_template('modules/create.html', form=form)

# NOTE: Stored filename will become modulename-versionstring.xxx
@modules.route('/upload/<name>', methods=['GET'])
def upload_module(name):
	if not g.user.is_authenticated:
		return render_template('modules/403.html', name=name)

	module = Module.get_by_name(name)

	if not g.user.id == module.owner:
		return render_template('modules/403.html', name=name)

	return render_template('modules/upload.html', module_name=name)

@modules.route('/name/<name>')
def info_module(name):
	module   = Module.get_by_name(name)

	is_owner = g.user.is_authenticated and g.user.id == module.owner
	
	if module is None:
		return render_template('modules/404.html', name=name)

	return render_template('modules/module.html', module_name = module.name)

# =============================================================================
# API endpoints
# NOTE: If a resource is created, the correct response code should be returned
# 	201 - Create
# NOTE: Location reference should be to the newly created resource
# [x] GET    to /api/modules -> list all modules
# [x] POST   to /api/modules -> Create/update module
# [/] DELETE to /api/modules -> Delete module
# [x] GET  to /api/modules/NewModule -> get info about module
# [/] POST to /api/modules/NewModule -> create/update verison
# [x] /api/modules/NewModule/latest -> Symlink to /xyz that is the latest version.
# [o] GET to /api/modules/NewModule/<version> -> Info specific to that version
# [x] GET  to /api/modules/NewModule/<version>/<file> -> Get path for that resource
# [/] POST to /api/modules/NewModule/<version>/<file> -> Update/Create that resouce
#
# TODO: It would be possible to cache common queries for a short 
# while to reduce load on cpu while maintaining quick updates
# 
# =============================================================================
@module_api.route('/', methods=['GET'])
def api_list_module():
	'''List all modules in database.
	Arguments:

	Optional arguments:
		username - String - Returns only modules for given owner.
	'''

	args     = util.parse_request_to_json(request)
	# username = util.html_escape_or_none(args['username'])
	username = util.html_escape_or_none(request.args.get('username'))

	if username:
		try:
			user = User.get_by_name(username)
		except UserNotFoundError:
			return util.make_json_error(data='No user with that name.')

		modules = Module.get_by_userid(user.id)
	else:
		modules = Module.query

	data = [ module.get_public_short_info() for module in modules ]

	return util.make_json_success(data=data)

@module_api.route('/', methods=['POST'])
def api_create_module():
	'''Create a module.
	Arguments:
		module_name - String - Name of module. If module does not 
		                       exist it will be created.

	Optional arguments:
		short_desc  - String - Short description of module. Will be included in
		                       listings.
		long_desc   - String - Longer description of module. Will not be 
		                       included in listings.
	'''
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	module_name = util.html_escape_or_none(args['name'])
	short_desc  = util.html_escape_or_none(args['short_desc'])
	long_desc   = util.html_escape_or_none(args['long_desc'])

	# picture        = args['picture']
	latest_version = None

	was_created = False
	module      = None
	try:
		module = Module.get_by_name(module_name)
		#TODO: Check ownership
	except ModuleNotFound:
		was_created = True
		module = Module(
			owner = g.user.id,
			name  = module_name,
			short_desc = short_desc,
			long_desc  = long_desc,

			latest_version = latest_version,
		)
		
	if short_desc is not None:
		module.short_desc = short_desc
	if long_desc is not None:
		module.long_desc = long_desc
	# if picture is not None:
	# 	module.picture = picture

	db.session.add(module)

	try:
		db.session.commit()
	except sqlalchemy.exc.IntegrityError as e:
		print(e)
		return util.make_json_error(msg='Invalid arguments.')

	if was_created:
		return util.make_json_success(msg='Module created.')
	else:
		return util.make_json_success(msg='Module updated.')

@module_api.route('/', methods=['DELETE'])
def api_delete_module():
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
	
	args        = util.parse_request_to_json(request)
	module_name = util.html_escape_or_none(args['name'])

	try:
		module = Module.get_by_name(module_name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	if g.user.id != module.owner:
		return util.make_json_error(msg='You do not own module {}.'.format(module_name))

	try:
		for version in Module.get_versions(module_name):
			db.session.delete(version)
		db.session.delete(module)
		db.session.commit()

		manager.delete_module(module)

		return util.make_json_success(msg='Module ' + module_name + ' deleted.')
	except:
		db.session.rollback()
		return util.make_json_error(msg='Error deleting module.')

@module_api.route('/<module_name>', methods=['GET'])
def api_info(module_name):
	'''Get meta-data for a given module.
	'''
	try:
		module = Module.get_by_name(module_name);
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found'.format(module_name));

	data = module.get_public_long_info()
	data['is_owner'] = g.user.is_authenticated and g.user.id == module.owner;
	return util.make_json_success(data=data);

@module_api.route('/<module_name>', methods=['POST'])
def api_version(module_name):
	'''Create a new version. Must be authenticated as owner.
	Arguments
		name - String - Required. Name of the new version.
		
		This function also takes and unspecified number of
		form-data encoded files.

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

	if not module.is_owner(g.user.username):
		return util.make_json_error(msg='You do not have the correct permissions.')

	try:		
		escaped_version = werkzeug.utils.escape(request.form['version'])
		files           = sum( request.files.listvalues(), [])

		# TODO: Argument validation should be standardised.
		if escaped_version == "":
			return util.make_json_error(msg='Version name cannot be empty.')

		manager.upload_version(module=module, sVersion=escaped_version, files=files)

	except manager.ModuleDuplicateVersionError as e:
		return util.make_json_error(msg='Version name already exists.')

	return util.make_json_success(msg='Success.')

# @module_api.route('/<module_name>/<version>', methods=['GET'])
# def api_version_get(module_name, version):
# 	return util.make_json_error(msg='Not implemented yet')

# @module_api.route('/<module_name>/<version>', methods=['POST'])
# def api_version_post(module_name, version):
# 	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/<module_name>/<version>/<file>', methods=['GET'])
def api_content_path_get(module_name, version, file):
	if version == 'latest':
		version = None

	try:
		module         = Module.get_by_name(module_name)
		module_version = module.get_version(version) if version is not None else None
		data           = manager.get_path_for_module_content(file, module, module_version)
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
