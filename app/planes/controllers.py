# Import flask dependencies
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g
from flask_login import login_required

import uuid

from app import db, util
from app.models import User
from app.planes.forms import CreatePlaneForm, PlanarAuthenticateForm
from app.planes.models import Plane, Session
from app.modules.models import Module
from app.modules.models import ModuleHasNoData

from app.modules import manager

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

	paths = {}
	try:
		paths['index.html'] = manager.get_path_for_module_content('index.html', module)
	except ModuleHasNoData:
		paths['index.html'] = ''
	try:
		paths['main.js'] = manager.get_path_for_module_content('main.js', module)
	except ModuleHasNoData:
		paths['main.js'] = ''

	try:
		module_path=manager.get_modver_web_path(module.name, None)
	except:
		return render_template('planes/module-not-found.html')

	# TODO: This should be rendered in a jinja sandbox environment.
	return render_template('planes/plane.html', 
		paths=paths,
		name=plane.get_name(),
		user=g.user.username,
		module_path=module_path,
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
		form = CreatePlaneForm()
		form.module.choices = form.getModules()
		if form.validate_on_submit():
			m = None
			if Module.query.filter_by(id=form.module.data).scalar() is not None:
				m = Module.query.filter_by(id=form.module.data).first()
			
			'''
			uid = uuid.uuid4()
			while Plane.query.filter_by(uuid=uid).scalar() is not None:
				uid = uuid.uuid4()
			'''

			plane = Plane(owner=g.user.id, password=form.password.data, module=m.id, data=None, name=form.name.data, public=not form.hidden.data)
			db.session.add(plane)
			db.session.commit()

			flash('Plane created')
			connect(g.user, plane)

			return redirect(url_for('planes.show_plane', name=form.name.data, password=form.password.data))
	else:
		return redirect(url_for('login'))

	return render_template('planes/create.html', title='Create Plane', form=form)

@planes.route('/name/<name>', methods=['GET', 'POST'])
@login_required
def show_plane(name):
	plane = Plane.query.filter_by(name=name).first()

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
	if username and (g.user is None or not g.user.is_authenticated):
		return util.make_json_error(msg='Not authenticated.')

	if username != g.user.username:
		return util.make_json_error(msg='No permission for this action.')

	if username:
		try:
			user = User.get_by_name(username)
		except UserNotFoundError:
			return util.make_json_error(data='No user with that name.')

		planes = list(map(lambda x: x.get_plane(), Session.get_sessions(user)))
	else:
		try:
			planes = Plane.get_planes()
		except Exception:
			return util.make_json_error()
	
	data = [p.get_public_info(user) for p in planes]
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

	password = util.html_escape_or_none(args['password'])
	module = util.html_escape_or_none(args['module'])
	name = util.html_escape_or_none(args['name'])
	public = util.html_escape_or_none(args['public'])
	
	if Module.query.filter_by(name=module).scalar() is None:
		return util.make_json_error(msg='Module does not exist.')
	if name is None:
		return util.make_json_error(msg='No plane name submitted.')
	if Plane.query.filter_by(name=name).scalar() is not None:
		return util.make_json_error(msg='A plane with that name already exists.')
	if public is None:
		public = False

	m = Module.query.filter_by(name=name).first()
	plane = Plane(
		owner=g.user.id, 
		password=passford, 
		module=m.id, 
		data=None, 
		name=name, 
		public=public
	)

	db.session.add(plane)

	try:
		db.session.commit()
	except sqlalchemy.exc.IntegrityError as e:
		return util.make_json_error(msg='Invalid arguments.')

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
		data - String - Data to store.
	'''

	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	data = util.html_escape_or_none(args['data'])
	plane = Plane.get_plane(plane_id)

	if plane.is_user_connected(g.user):
		plane.set_data(data)
		try:
			db.session.commit()
		except sqlalchemy.exc.IntegrityError as e:
			return util.make_json_error(msg='Invalid arguments.')
		return util.make_json_success(msg='Data stored successfully.')
	else:	
		return util.make_json_error(msg='Not owner of plane.')

@planes_api.route('/<plane_id>/data', methods=['GET'])
def api_get_data(plane_id):
	'''Get information for plane.
	Returns
		data - 
	'''
	if g.user is None or not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	plane = Plane.get_plane(plane_id)

	if plane.is_user_connected(g.user):
		data = plane.get_data()
		return util.make_json_success(data=data)
	else:
		return util.make_json_error(msg='No session to plane.')
