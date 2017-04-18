#!/usr/bin/env python3
from app import db, models
from app.planes import models as plane_models
from app.modules import models as module_models
from app         import models as user_models
from app.modules import manager as manager

from config import RETHINK_DB_PORT

# TODO: The add_user etc. should use manager functions in the same style as 
# 	app.modules.manager for adding module versions.

def add_user(name, password, email):
	'''Add a user to the database
	'''
	print ('Add user ' + name + '')
	try:
		user_models.User.get_by_name(name)
		print ('\tSkipping -- owner _does_ exist.')
		return False
	except user_models.UserNotFoundError:
		pass

	try:
		u = models.User(username=name, password=password, email=email)
		db.session.add(u)
		db.session.commit()
	except Exception as e:
		print ('\tSkipping -- unknown error.')
		return False

	return True

def add_module(owner_name, module_name):
	'''Add a module to the database
	'''
	print ('Add module ' + module_name + '')
	try:
		module_models.Module.get_by_name(module_name)
		print ('\tSkipping -- module exists.')
		return False
	except module_models.ModuleNotFound:
		pass

	try:
		owner = user_models.User.get_by_name(owner_name)
	except user_models.UserNotFoundError:
		print ('\tSkipping -- owner does not exist.')
		return False

	try:
		module = module_models.Module(
			owner      = owner.id,
			name       = module_name,

			latest_version=None,
		)
		db.session.add(module)
		db.session.commit()
	except Exception as e:
		print ('\tSkipping -- unknown error.')
		print ('\t'+str(e))
		return False
	return True

def add_module_version(module_name, version_name, path):
	'''Add a verison to a given module
	'''
	print ('Add version '+version_name+' to '+module_name+'.')
	try:
		module = module_models.Module.get_by_name(module_name)
		if not module.has_version(version_name):
			manager.upload_version_path(module, version_name, path)
		else:
			print ('\tSkipping -- version already exists.')	
			return False
	except module_models.ModuleNotFound:
		print ('\tSkipping -- module not found.')
		return False
	except Exception as e:
		print ('\tSkipping -- unknown exception.')
		print ('\t'+str(e))
		return False
	return True

def add_plane(plane_name,  module_name, owner_name, password, public):
	'''Add a plane to the database
	'''
	print ('Add plane '+plane_name+' ')
	try:
		user    = user_models.User.get_by_name(owner_name)
		module  = module_models.Module.get_by_name(module_name)
		version = module.get_latest_version()

		plane = plane_models.Plane(
			owner    = user.id,
			password = password,
			module   = module.id,
			name     = plane_name,
			version  = version.id,
			public   = public
		)

		db.session.add(plane)
		db.session.commit()

		r.db('planeshift')                                \
			.table('planes')                              \
			.insert({'id': plane.get_id(), 'data': None}) \
			.run(rethink_connection)

	except user_models.UserNotFoundError:
		print ('\tSkipping -- user '+owner_name+' not found.')
		return False
	except module_models.ModuleNotFound:
		print ('\tSkipping -- module '+module_name+' not found.')
		return False
	except module_models.ModuleVersionNotFound:
		print ('\tSkipping -- latest version for '+module_name+' not found.')
		return False
	except Exception as e:
		print ('\tSkipping -- unknown exception.')
		print ('\t'+str(e))
		return False
	return True


# Set up rethink db
####################################################################
print()
print('Setting up rethink db...')
print('='*80)
import rethinkdb as r
rethink_connection = r.connect( "localhost", RETHINK_DB_PORT)
try:
	r.db_drop('planeshift').run(rethink_connection)
except Exception:
	pass
r.db_create('planeshift').run(rethink_connection)
r.db("planeshift").table_create("planes").run(rethink_connection)

# Add test users
####################################################################
print()
print('Adding users...')
print('='*80)
add_user('john', 'pass', 'john@test.com')
add_user('test', 'test', 'test@test.com')

# Add test modules
####################################################################
# add_module(
# 	owner_name  = ,
# 	module_name = ,
# 	short       = ,
# 	long        = ,
# )
print()
print('Adding modules...')
print('='*80)

add_module(
	owner_name  = 'john',
	module_name = 'Dice Roller',
)

add_module(
	owner_name  = 'john',
	module_name = 'Settlers of Catan',
)

add_module(
	owner_name  = 'john',
	module_name = 'Tutorial Module',
)
	
# Add module versions
####################################################################
print()
print('Adding module versions...')
print('='*80)
add_module_version("Dice Roller", "1.0.0", "external/dice")
add_module_version("Settlers of Catan", "1.0.0", "external/catan")
add_module_version("Tutorial Module", "1.0.0", "external/test-module")

# Add test planes
####################################################################
print()
print('Adding planes...')
print('='*80)

add_plane(
	plane_name  = 'Settlers Demo Room',
	module_name = 'Settlers of Catan',
	owner_name  = 'john',
	password    = None,
	public      = True,
)

add_plane(
	plane_name  = 'Astral Plane',
	module_name = 'Dice Roller',
	owner_name  = 'john',
	password    = None,
	public      = True,
)

add_plane(
	plane_name  = 'test-plane',
	module_name = 'Tutorial Module',
	owner_name  = 'john',
	password    = None,
	public      = True,
)

add_plane(
	plane_name  = 'Haven',
	module_name = 'Dice Roller',
	owner_name  = 'john',
	password    = 'iomedae',
	public      = False,
)

add_plane(
	plane_name  = 'Hell',
	module_name = 'Dice Roller',
	owner_name  = 'john',
	password    = 'asmodeus',
	public      = False,
)

