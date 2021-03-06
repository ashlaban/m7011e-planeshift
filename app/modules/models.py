
from app import db
from app.models import User

class ModuleNotFound(ValueError):
	'''Raise when searching for a non-existant module.'''

class ModuleVersionNotFound(ValueError):
	'''Raise when searching for a non-existant version of a module.'''

# NOTE: This is a more specific version of "ModuleVersionNotFound".
class ModuleHasNoData(ValueError):
	'''Raise when no data is uploaded for a module.'''

# NOTE: Version strings needs to be secure (db_escaped) and url safe (url_escaped).
#  It is possible that url_escape provides sufficient db escape.
class ModuleVersion(db.Model):
	__tablename__ = 'module_versions'
	id             = db.Column(db.Integer   , primary_key=True)
	module_id      = db.Column(db.Integer   , db.ForeignKey('module.id'), nullable=False)
	version_string = db.Column(db.String(16), nullable=False)
	db.UniqueConstraint(module_id, version_string)

	@staticmethod
	def get_by_id(id):
		version = ModuleVersion.query.filter_by(id=id).first()
		if version is None:
			raise ModuleVersionNotFound()
		return version

	@staticmethod
	def get_all_for_module_id(module_id):
		lst = ModuleVersion.query.filter_by(module_id=module_id)
		return lst

	@staticmethod
	def get_by_name(module_id, name):
		version = ModuleVersion.query.filter_by(module_id=module_id, version_string=name).first()
		if version is None:
			raise ModuleVersionNotFound()
		else:
			return version

	def get_escaped_version(self):
		return str(self.version_string)

class Module(db.Model):
	id      = db.Column(db.Integer    , primary_key=True)
	owner   = db.Column(db.Integer    , db.ForeignKey('user.id'), nullable=False)
	# picture = db.Column(db.Text()) # TODO: size should be limited

	name       = db.Column(db.String(64) , nullable=False)
	short_desc = db.Column(db.String(500))
	long_desc  = db.Column(db.Text())

	latest_version     = db.Column(db.ForeignKey('module_versions.id'))

	@staticmethod
	def get_all(limit=None):
		if limit is None:
			return Module.query
		return Module.query.limit(limit)

	@staticmethod
	def get_by_name(module_name):
		module = Module.query.filter_by(name=module_name).first()
		if module is None:
			raise ModuleNotFound()
		return module

	@staticmethod
	def get_by_userid(userid):
		return Module.query.filter_by(owner=userid)

	@staticmethod
	def get_versions(module_name):
		module   = Module.get_by_name(module_name)
		versions = ModuleVersion.query.filter_by(module_id=module.id)
		return versions
	
	@staticmethod
	def get_versions_for_module_id(module_id):
		versions = ModuleVersion.get_all_for_module_id(module_id)
		return versions

	def has_version(self):
		return self.latest_version != None

	def has_version(self, version_string):
		version_list = Module.get_versions(self.name)
		for version in version_list:
			if version.version_string == version_string:
				return True
		return False

	def get_owner(self):
		return User.get_by_id(self.owner)

	def is_owner(self, user):
		if not isinstance(user, User):
			user = User.get_by_name(user)
		return self.owner == user.id

	def get_version(self, name):
		return ModuleVersion.get_by_name(self.id, name)

	def get_latest_version(self):
		module_version = ModuleVersion.get_by_id(self.latest_version)
		return module_version

	def get_picture_path(self):
		from app.modules.manager import get_path_for_module_content
		try:
			return get_path_for_module_content('icon', self)
		except ModuleHasNoData:
			return ''

	def get_public_short_info(self):
		
		data = {
			'name'      : self.name,
			'short_desc': self.short_desc,
			'owner'     : self.get_owner().username,

			'picture'   : self.get_picture_path(),
		}
		return data

	def get_public_long_info(self):
		try:
			version_string = self.get_latest_version().get_escaped_version()
		except ModuleVersionNotFound:
			version_string = ''	

		versions = Module.get_versions_for_module_id(self.id)
		versions = [v.version_string for v in versions]

		data = {
			'name'      : self.name,
			'short_desc': self.short_desc,
			'long_desc' : self.long_desc,
			'owner'     : self.get_owner().username,
			
			'picture'   : self.get_picture_path(),
			'latest_version': (self.latest_version, version_string),
			'versions'      : versions
		}
		return data

	def __repr__(self):
		return '<Module %r>'.format(self.name)
