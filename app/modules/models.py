
from app import db

class ModuleVersions(db.Model):
	__tablename__ = 'module_versions'
	id             = db.Column(db.Integer   , primary_key=True)
	module_id      = db.Column(db.Integer   , db.ForeignKey('module.id'), nullable=False)
	version_string = db.Column(db.String(16), nullable=False)
	db.UniqueConstraint(module_id, version_string)

	@staticmethod
	def get_by_id(id):
		return ModuleVersions.query.filter_by(id=id).first()

	def get_escaped_version(self):
		return str(self.version_string)

class Module(db.Model):
	id      = db.Column(db.Integer    , primary_key=True)
	owner   = db.Column(db.Integer    , db.ForeignKey('user.id'))
	picture = db.Column(db.Text()) # TODO: size should be limited

	name       = db.Column(db.String(64))
	short_desc = db.Column(db.String(128))
	long_desc  = db.Column(db.Text()     )

	latest_version     = db.Column(db.ForeignKey('module_versions.id'))

	@staticmethod
	def get_by_name(module_name):
		return Module.query.filter_by(name=module_name).first()

	@staticmethod
	def get_versions(module_name):
		module   = Module.get_module_by_name(module_name)
		versions = ModuleVersions.query.filter_by(module_id=module.id)
		return versions
	
	@staticmethod
	def get_versions_for_module_id(module_id):
		versions = ModuleVersions.query.filter_by(module_id=module_id)
		return versions

	def get_escaped_version(self):
		module_versions = ModuleVersions.get_by_id(self.latest_version)
		return module_versions.get_escaped_version()

	def __repr__(self):
		return '<Module %r>'.format(self.name)
