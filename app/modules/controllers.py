# Import flask dependencies
from flask import Blueprint, render_template
#, request, render_template, flash, g, session, redirect, url_for

from app import db
from app.modules.models import Module

# Define the blueprint: 'auth', set its url prefix: app.url/auth
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

@modules.route('/<name>')
def info_module(name):
	module = db.session.query(Module).filter_by(name=name).first()
	
	if module is None:
		return render_template('modules/404.html', name=name)

	return render_template('modules/module.html', module=module)

# API endpoints
@api.route('/create')
def api_create_module():
	pass

@api.route('/upload_version')
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

