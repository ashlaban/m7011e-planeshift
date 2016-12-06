
from app import db

versions = db.Table('module_versions',
	db.Column('id'            , db.Integer   , primary_key=True),
    db.Column('module_id'     , db.Integer   , db.ForeignKey('module.id')),
    db.Column('version_string', db.String(16))
)

class Module(db.Model):
	id      = db.Column(db.Integer    , primary_key=True)
	owner   = db.Column(db.Integer    , db.ForeignKey('user.id'))
	picture = db.Column(db.Text()) # TODO: size should be limited

	name       = db.Column(db.String(64))
	short_desc = db.Column(db.String(128))
	long_desc  = db.Column(db.Text()     )

	latest_version     = db.Column(db.ForeignKey('module_versions.id'))

	# @property
	# def name(self):
	# 	return unicode(self.name)

	# @property
	# def short_description(self):
	# 	return unicode(self.short_description)

	# @property
	# def long_description(self):
	# 	return unicode(self.long_description)

	# @property
	# def owner(self):
	# 	return unicode(self.owner)

	# @property
	# def picture(self):
	# 	return unicode(self.picture)

	# @property
	# def latest_version(self):
	# 	return unicode(self.latest_version)

	# def get_available_versions(self):
	# 	pass

	# def get_id(self):
	# 	return unicode(self.id)
	
	def __repr__(self):
		return '<Module %r>'.format(self.name)
