# Import flask dependencies
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g

import uuid

from app import db
from app.planes.forms import CreatePlaneForm
from app.planes.models import Plane
from app.modules.models import Module

from app.modules import manager

# Define the blueprint: 'auth', set its url prefix: app.url/auth
planes = Blueprint('planes', __name__, url_prefix='/planes')
api     = Blueprint('planes', __name__, url_prefix='/api')

# Views
@planes.route('/')
def list_plane():
	planes = Plane.get_planes()
	return render_template('planes/index.html', planes=planes)

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
			return redirect(url_for('planes.join_plane', name=form.name.data))
	else:
		return redirect(url_for('login'))

	return render_template('planes/create.html', title='Create Plane', form=form)

@planes.route('/name/<name>')
def join_plane(name):
	plane = Plane.query.filter_by(name=name).first()
	
	if plane is None:
		return render_template('planes/404.html', name=name)

	module = plane.get_module()

	paths = {}
	paths['html'] = manager.get_path_for_module_content('html', module.name)
	paths['css']  = manager.get_path_for_module_content('css' , module.name)
	paths['js']   = manager.get_path_for_module_content('js'  , module.name)
	return render_template('planes/plane.html', paths=paths)

# API endpoints
@api.route('/create')
def api_create_plane():
	pass
