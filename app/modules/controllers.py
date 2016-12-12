# Import flask dependencies
from flask import Blueprint, render_template, redirect, flash, url_for, g
#, request, flash, g, session, url_for

from app import app
import werkzeug

from app import db
from app.modules.models import Module
from app.modules.forms  import UploadForm, VersionForm
from app.modules import manager

# Define blueprints
modules = Blueprint('modules', __name__, url_prefix='/modules')
api     = Blueprint('modules', __name__, url_prefix='/api')

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
	module = Module.get_by_name(name)

	if not g.user.is_authenticated:
		return redirect(url_for('login'))

	if not g.user.id == module.owner:
		return render_template('modules/403.html', name=name)

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

	# TODO: If authenticated, show upload new version button + form.
	
	if module is None:
		return render_template('modules/404.html', name=name)

	return render_template('modules/module.html', module=module, form=form, is_owner=is_owner)

# API endpoints
@api.route('/create')
def api_create_module():
	pass

@api.route('/upload_version', methods=['POST'])
def api_upload_module():
	pass

@api.route('/get')
def api_get_module_info():
	'''Returns information for module with name+version.
	'''
	pass

@api.route('/getcontent')
def api_get_module_content():
	'''Returns the .js file associated with a module name+version.
	'''
	pass

# Perhaps this should not 
# @api.route('/get_path')
# def api_get_module_path():
# 	pass

