# Import flask dependencies
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g
from flask_login import login_required

import uuid
import json
import os

from app import db, util
from app.models import User
from app.planes.forms import PlaneCreateForm, PlanarAuthenticateForm
from app.planes.models import Plane, Session
from app.modules.models import Module
from app.modules.models import ModuleHasNoData, ModuleVersionNotFound

from app.modules import manager

from config import RETHINK_DB_PORT

import sqlalchemy

# Define the blueprint: 'auth', set its url prefix: app.url/auth
planes     = Blueprint('planes', __name__, url_prefix='/planes')
planes_api = Blueprint('planes_api', __name__, url_prefix='/api/planes')

# Helper functions
def connect(user, plane):
	if Session.get_session(user, plane) is None:
		s = Session(user=user.id , plane=plane.get_id())
		db.session.add(s)
		db.session.commit()

def disconnect(user, plane):
	s = Session.get_session(user, plane)
	if s is not None:
		db.session.delete(s)
		db.session.commit()

def show_plane_helper(plane):
	if plane is None:
		return render_template('planes/404.html', name=name)

	module = plane.get_module()
	if module is None:
		return render_template('planes/module-not-found.html')

	web_paths = {}
	version_name = plane.get_version().get_escaped_version()
	try:
		module_path = manager.get_modver_web_path(module.name, version_name)
	except ModuleHasNoData:
		return render_template('planes/module-not-found.html')

	if not manager.exists_path_for_module_content('main.js', module, version_name):
		return render_template('planes/module-not-found.html')

	# TODO: This should be rendered in a jinja sandbox environment.
	return render_template('planes/plane.html', 
		plane_name      = plane.get_name(),
		current_user    = g.user.username,
		module_path     = module_path,
		connected_users = plane.get_users(),
	)

# Views
@planes.route('/')
def list_plane():
	planes = Plane.get_planes()
	public = []
	for plane in planes:
		if plane.is_public():
			public.append(plane)
	return render_template('planes/index.html', planes=public)

@planes.route('/create', methods=['GET', 'POST'])
def create_plane():
	if g.user is not None and g.user.is_authenticated:
		form = PlaneCreateForm()
		return render_template('planes/create.html', title='Create Plane', form=form)
	else:
		return redirect(url_for('login'))

@planes.route('/name', methods=['GET'])
@planes.route('/name/', methods=['GET'])
def plane_page_not_found_upload():
	return render_template('/404.html')

@planes.route('/name/<name>', methods=['GET', 'POST'])
@login_required
def show_plane(name):
	plane = Plane.query.filter_by(name=name).first()

	if plane is None:
		return render_template('planes/404.html', name=name)

	if plane and plane.has_password() and not plane.is_user_connected(g.user):
		form = PlanarAuthenticateForm(plane_name=plane.name)
		if form.validate_on_submit():
			connect(g.user, plane)
			return show_plane_helper(plane)
		return render_template('planes/authenticate.html', title='Authenticate', form=form)
	else:
		connect(g.user, plane)
		return show_plane_helper(plane)



# API endpoints
@planes_api.route('/', methods=['GET'])
def api_list():
	'''List all planes in database
	'''
	username = util.html_escape_or_none(request.args.get('username'))
	if username:
		if username and (g.user is None or not g.user.is_authenticated):
			return util.make_json_error(msg='Not authenticated.')

		if username != g.user.username:
			return util.make_json_error(msg='No permission for this action.')

		try:
			user = User.get_by_name(username)
		except UserNotFoundError:
			return util.make_json_error(data='No user with that name.')

		planes = list(map(lambda x: x.get_plane(), Session.get_sessions(user)))
	else:
		try:
			planes = Plane.get_public_planes()
		except Exception:
			return util.make_json_error()
	
	data = [p.get_public_info(g.user) for p in planes]
	return util.make_json_success(data=data)

@planes_api.route('/', methods=['POST'])
def api_create_plane():
	'''Create a plane.
	Arguments
		password - String - Password to join plane.
		module - String - Required. Name of module to load.
		name - String - Required. Name of plane to be created.
		public - Boolean - True if plane should be public, False if not.
	'''

	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	password     = util.html_escape_or_none(args['password'])
	module_name  = util.html_escape_or_none(args['module'])
	plane_name   = util.html_escape_or_none(args['name'])
	hidden       = util.html_escape_or_none(args['hidden'])

	module = Module.query.filter_by(name=module_name).first()

	if module is None:
		return util.make_json_error(msg='Module does not exist.')
	if plane_name is None or plane_name == '':
		return util.make_json_error(msg='No plane name submitted.')
	if Plane.query.filter_by(name=plane_name).scalar() is not None:
		return util.make_json_error(msg='A plane with that name already exists.')
	
	try:
		version = module.get_latest_version()
	except ModuleVersionNotFound:
		return util.make_json_error(msg='Module has no version attached.')

	hidden = (hidden == 'True')

	plane = Plane(
		owner    = g.user.id, 
		password = password, 
		module   = module.id,
		version  = version.id,
		data     = None, 
		name     = plane_name, 
		public   = not bool(hidden),
	)

	db.session.add(plane)

	try:
		db.session.commit()

		import rethinkdb as r
		rethink_connection = r.connect( "localhost", RETHINK_DB_PORT)
		r.db('planeshift')                                \
			.table('planes')                              \
			.insert({'id': plane.get_id(), 'data': None}) \
			.run(rethink_connection)

	except sqlalchemy.exc.IntegrityError as e:
		db.session.rollback()
		return util.make_json_error(msg='Invalid arguments.')
	except Exception as s:
		db.session.rollback()
		return util.make_json_error(msg='Internal error.')

	connect(g.user, plane)
	return util.make_json_success(msg='Plane created.')

@planes_api.route('/<plane>', methods=['POST'])
def api_connect(plane):
	'''Create a session between user and plane.
	Arguments
		password - String - Password to plane if such exist.
	'''

	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	password = Plane.get_plane(util.html_escape_or_none(args['password']))
	planar = Plane.get_plane(plane)

	if planar.has_password():
		if planar.password_matching(password):
			connect(g.user, planar)
			return util.make_json_success(msg='Connected.')
		else:
			return util.make_json_error(msg='Incorrect planar password.')
	else:
		connect(g.user, planar)
		return util.make_json_success(msg='Connected.')

@planes_api.route('/<plane>', methods=['DELETE'])
def api_disconnect(plane):
	'''Remove a session between current user and <plane>.
	'''

	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	planar = Plane.get_plane(plane)

	disconnect(g.user, plane)

	return util.make_json_success(msg='Disconnected.')

@planes_api.route('/<plane_id>', methods=['GET'])
def api_get_plane(plane_id):
	'''Get information for plane.
	Returns
		is_owner - Boolean - True if current user is owner of plane, False if not.
		module_name - String - Name of module related to plane.
		module_version - String - Latest version of module related to plane. Note: the actual version when the plane is created and possibility to update should be added in the future.
		plane_data - String - Data stored on plane.
		name - String - Name of plane.
		public - Boolean - True if plane is public, False if not.
		users - List of String - List of names of users that are connected to plane.
	'''
	print(plane_id)
	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	plane = Plane.get_plane(plane_id)
	if plane is None:
		return util.make_json_error(msg='Plane does not exist.')

	if plane.is_user_connected(g.user):
		return util.make_json_success(data=plane.get_public_info(g.user))
	else:
		return util.make_json_error(msg='Unauthorised. Did you join the plane?')

@planes_api.route('/<plane_id>/data', methods=['POST'])
def api_store_data(plane_id):
	'''Store data on plane.
	Arguments
		data   - String - 
	'''

	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args  = util.parse_request_to_json(request)
	data  = args['data']
	plane = Plane.get_plane(plane_id)

	if plane.is_user_connected(g.user):
		try:
			plane.set_data(data)
		except r.errors.ReqlDriverCompileError:
			return util.make_json_error(msg='Invalid request.')
		except:
			return util.make_json_error(msg='Error setting data.')

		return util.make_json_success(msg='Data stored successfully.')
	else:	
		return util.make_json_error(msg='Not connected to plane.')

@planes_api.route('/<plane_id>/data', methods=['GET'])
def api_get_data(plane_id):
	'''Get information for plane.
	Arguments
		key   - String - JSON key supporting nested selection.
	'''
	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args  = request.args
	key   = args['key']
	try:
		key   = json.loads(key)
	except:
		key = True

	plane = Plane.get_plane(plane_id)

	if plane.is_user_connected(g.user):
		try:
			data = plane.get_data(key)
			return util.make_json_success(data=data)
		except:
			return util.make_json_error(msg='Error retrieving data for key: ' + str(key))
	else:
		return util.make_json_error(msg='No session to plane.')
