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

# Define blueprints
modules    = Blueprint('modules_mod', __name__, url_prefix='/modules')
module_api = Blueprint('modules_api', __name__, url_prefix='/api/modules')

# Views
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

# API endpoints
@module_api.route('/create', methods=['POST'])
def api_create_module():
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = request.get_json()
	args = collections.defaultdict(lambda:None, **args) if args is not None else collections.defaultdict(lambda:None)

	module_name = werkzeug.utils.escape(args['name']) if args['name'] is not None else None
	short_desc  = werkzeug.utils.escape(args['short_desc'])
	long_desc   = werkzeug.utils.escape(args['long_desc'])

	picture        = args['picture']
	latest_version = None

	module = Module(
		owner = g.user.id,
		name  = module_name,
		short_desc = short_desc,
		long_desc  = long_desc,

		picture        = picture,
		latest_version = latest_version,
	)

	db.session.add(module)

	try:
		db.session.commit()
	except sqlalchemy.exc.IntegrityError as e:
		return util.make_json_error(msg='Invalid arguments.')

	return util.make_json_success(msg='Module created.')

@module_api.route('/update/<name>/version', methods=['POST'])
def api_update_version(name):
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/update/<name>/short_desc', methods=['POST'])
def api_update_short_desc(name):
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/update/<name>/long_desc', methods=['POST'])
def api_update_long_desc(name):
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/update/<name>/picture', methods=['POST'])
def api_update_picture(name):
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/<name>/delete', methods=['POST'])
def api_delete_module(name):
	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')
	
	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(module_name))

	if g.user.id != module.owner:
		return util.make_json_error(msg='You do not own module {}.'.format(module_name))

	return util.make_json_error(msg='Not implemented yet')

@module_api.route('/list')
def api_list_modules():
	'''List all modules in database'''
	try:
		modules = Module.query
	except Exception:
		return util.make_json_error()

	# TODO: It would be possible to cache common queries for a short 
	# while to reduce load on cpu while maintaining quick updates
	data = [ module.get_public_short_info() for module in modules ]

	return util.make_json_success(data=data)

@module_api.route('/get/<name>', defaults={'version': None})
@module_api.route('/get/<name>/<version>')
def api_get_module_info(name, version):
	'''Returns information for module with name+version.
	'''
	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found'.format(name))

	data = module.get_public_long_info()
	return util.make_json_success(data=data)

@module_api.route('/pic/<name>', defaults={'version': None})
@module_api.route('/pic/<name>/<version>')
def api_get_module_pic(name, version):
	try:
		module = Module.get_by_name(name)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found'.format(name))

	if version is None:
		return util.make_json_success(data=module.picture)
	else:
		try:
			version = module.get_version(name=version)
		except ModuleVersionNotFound:
			return util.make_json_error(msg='Version {} not found'.format(version))
		return util.make_json_error(msg='Pics are not stored by version currently')

@module_api.route('/js/<name>'            , defaults={'ext': 'js', 'version': None})
@module_api.route('/css/<name>'           , defaults={'ext': 'css', 'version': None})
@module_api.route('/html/<name>'          , defaults={'ext': 'html', 'version': None})
@module_api.route('/js/<name>/<version>'  , defaults={'ext': 'js'})
@module_api.route('/css/<name>/<version>' , defaults={'ext': 'css'})
@module_api.route('/html/<name>/<version>', defaults={'ext': 'html'})
def api_get_module_js(name=None, version=None, ext=None):
	try:
		module         = Module.get_by_name(name)
		module_version = module.get_version(version) if version is not None else None
		data           = manager.get_path_for_module_content(ext, module, module_version)
	except ModuleNotFound:
		return util.make_json_error(msg='Module {} not found.'.format(name))
	except ModuleVersionNotFound:
		return util.make_json_error(msg='Version {} not found for module {}'.format(version, name))
	except ModuleHasNoData:
		return util.make_json_error(msg='No version uploaded for module {} yet!'.format(name))
	
	return util.make_json_success(data=data)
