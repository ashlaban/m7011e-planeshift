#!/usr/bin/env python3
from app import db, models
from app.planes import models as plane_models
from app.modules import models as module_models

import uuid

# Set up rethink db
####################################################################
import rethinkdb as r
rethink_connection = r.connect( "localhost", 28015)
try:
	r.db_drop('planeshift').run(rethink_connection)
except Exception:
	pass
r.db_create('planeshift').run(rethink_connection)
r.db("planeshift").table_create("planes").run(rethink_connection)

# Add test users
####################################################################
print('Adding users...')
if db.session.query(models.User).filter(models.User.username=='john').first() is None:
	print('User: john')
	u = models.User(username='john', password='pass', email='john@email.com')
	db.session.add(u)
	db.session.commit()

if db.session.query(models.User).filter(models.User.username=='test').first() is None:
	print('User: test')
	u = models.User(username='test', password='test', email='test@test.com')
	db.session.add(u)
	db.session.commit()

# Add test modules
####################################################################
from app.modules import models as module_models
user_john = db.session.query(models.User).filter(models.User.username=='john').first()

if db.session.query(module_models.Module).filter(module_models.Module.name=='TestModule').first() is None:
	module1 = module_models.Module(
		owner   = user_john.id,
		name       = 'TestModule',
		short_desc = 'Short description of a module',
		long_desc  = 'This is a test module long description',

		latest_version=None,
	)
	db.session.add(module1)

if db.session.query(module_models.Module).filter(module_models.Module.name=='FakeThing').first() is None:
	module2 = module_models.Module(
		owner   = user_john.id,
		name       = 'FakeThing',
		short_desc = 'Lorem ipsum sit amet. Praise be Amun-Ra!',
		long_desc  = 'This is a test module long description',

		latest_version=None,
	)
	db.session.add(module2)

db.session.commit()

# Add test planes
####################################################################
user_john = db.session.query(models.User).filter(models.User.username=='john').first()
test_module = db.session.query(module_models.Module).filter(module_models.Module.name=='TestModule').first()

'''
uid = []
for i in range(3):
	x = uuid.uuid4()
	
	while x in uid:
		x = uuid.uuid4()
	
	uid.append(x)
#debug stuff
for j in uid:
	print j.hex
'''

plane1 = plane_models.Plane(
	owner = user_john.id,
	password = None,
	module = test_module.id,
	name = 'Astral Plane',
	public = True)

plane2 = plane_models.Plane(
	owner = user_john.id,
	password = 'iomedae',
	module = test_module.id,
	name = 'Haven',
	public = False)

plane3 = plane_models.Plane(
	owner = user_john.id,
	password = 'asmodeus',
	module = test_module.id,
	name = 'Hell',
	public = False)

db.session.add(plane1)
db.session.add(plane2)
db.session.add(plane3)
db.session.commit()

