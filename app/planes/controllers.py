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

# Define the blueprint: 'auth', set its url prefix: app.url/auth
planes = Blueprint('planes', __name__, url_prefix='/planes')
plane_api = Blueprint('planes', __name__, url_prefix='/api/planes')

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

def join(plane):
	if plane is None:
		return render_template('planes/404.html', name=name)

	module = plane.get_module()

	paths = {}
	try:
		paths['html'] = manager.get_path_for_module_content('html', module)
	except ModuleHasNoData:
		paths['html'] = ''
	try:
		paths['css'] = manager.get_path_for_module_content('css', module)
	except ModuleHasNoData:
		paths['css'] = ''
	try:
		paths['js'] = manager.get_path_for_module_content('js', module)
	except ModuleHasNoData:
		paths['js'] = ''

	connect(g.user, plane)
	return render_template('planes/plane.html', paths=paths)

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

			plane = Plane(owner=g.user.id, password=form.password.data, module=m.id, data=None, name=form.name.data, public=form.public.data)
			db.session.add(plane)
			db.session.commit()

			flash('Plane created')
			return redirect(url_for('planes.join_plane', name=form.name.data, password=form.password.data))
	else:
		return redirect(url_for('login'))

	return render_template('planes/create.html', title='Create Plane', form=form)

@planes.route('/name/<name>', methods=['GET', 'POST'])
@login_required
def join_plane(name):
	plane = Plane.query.filter_by(name=name).first()

	if plane.has_password():
		form = PlanarAuthenticateForm(plane_name=plane.name)
		if form.validate_on_submit():
			return join(plane)
		return render_template('planes/authenticate.html', title='Authenticate', form=form)
	else:
		return join(plane)

# API endpoints
@plane_api.route('/', methods=['GET'])
def api_list():
	'''List all planes in database
	'''
	try:
		planes = Plane.get_planes()
	except Exception:
		return util.make_json_error()

	data = [p.get_name() for p in planes]

	return util.make_json_success(data=data)

@plane_api.route('/create', methods=['POST'])
def api_create_plane():
	'''Create a plane.
	Arguments
		password - String - Password to join plane.
		module - String - Required. Name of module to load.
		name - String - Required. Name of plane to be created.
		public - Boolean - True if plane should be public, False if not.
	'''

	if not g.user.is_authenticated:
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

@plane_api.route('/connect', methods=['POST'])
def api_connect():
	'''Create a session between user and plane.
	Arguments
		plane - String - Required. Name of plane.
	'''

	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	plane = Plane.get_plane(util.html_escape_or_none(args['plane']))

	connect(g.user, plane)

	return util.make_json_success(msg='Connected.')

@plane_api.route('/disconnect', methods=['POST'])
def api_disconnect():
	'''Remove a session between user and plane.
	Arguments
		plane - String - Required. Name of plane.
	'''

	if not g.user.is_authenticated:
		return util.make_json_error(msg='Not authenticated.')

	args = util.parse_request_to_json(request)

	plane = Plane.get_plane(util.html_escape_or_none(args['plane']))

	disconnect(g.user, plane)

	return util.make_json_success(msg='Disconnected.')

@plane_api.route('/sessions', methods=['GET'])
def api_sessions():
	'''Returns all active sessions
	Returns
		data - List of tuples containing user names and plane names that are connected.
	'''
	data = [(s.get_user().username, s.get_plane().get_name()) for s in Session.get_sessions()]
	return util.make_json_success(data=data)

@plane_api.route('/sessions/<plane>', methods=['GET'])
def api_sessions_by_plane(plane):
	'''Returns all active sessions related to plane
	Returns
		data - List of tuples containing user names and plane names that are connected.
	'''
	data = [(s.get_user().username, s.get_plane().get_name()) for s in Session.get_users_for_plane(plane)]
	return util.make_json_success(data=data)

@plane_api.route('/sessions/<user>', methods=['GET'])
def api_sessions_by_user(user):
	'''Returns all active sessions related to user
	Returns
		data - List of tuples containing user names and plane names that are connected.
	'''
	data = [(s.get_user().username, s.get_plane().get_name()) for s in Session.get_sessions(user)]
	return util.make_json_success(data=data)

@plane_api.route('/sessions/<plane>/<user>', methods=['GET'])
def api_get_session(plane, user):
	'''Returns active session related to plane and user
	Returns
		data - List of tuples containing user names and plane names that are connected.
	'''
	data = [(s.get_user().username, s.get_plane().get_name()) for s in Session.get_session(user, plane)]
	return util.make_json_success(data=data)
