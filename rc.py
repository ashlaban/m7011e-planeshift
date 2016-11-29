#
# TODO: Rename config.py and move the current config.py to a /db folder?
# 
# Note logging is not available in this file, so don't try to. (It is required
# by log.py which sets up logging path etc.)
#

import json

def from_str_to_bool(x):
	if type(x) is not str:
		raise ValueError('Input data ({}) is not string.'.format(x))

	if x == "True" or x == "true":
		return True

	if x == "False" or x == "false":
		return False

	raise ValueError('Value cannot be conveted to bool. "{}" is not "True" or "False".'.format(x))
	return

def from_str_to_loglevel(x):
	import logging
	# TODO: Better way of doing in -- rc.ConfigutrationManager.enforce_type()
	if x.lower() in ['debug']:
		return logging.DEBUG
	if x.lower() in ['info']:
		return logging.INFO
	if x.lower() in ['warn']:
		return logging.WARN
	if x.lower() in ['error']:
		return logging.ERROR

	raise ValueError('Input value {} not in ["debug", "info", "warn", "error"]')
	return

CONFIG_PATH   = './config.json'
DEBUG         = False

WEB_DEFUALTS = {
	'host' : '0.0.0.0',
	'port' : '8081',
	'debug': 'False',
}

LOG_DEFUALTS = {}

DEFAULTS = {
	'web': WEB_DEFUALTS,
	'log': LOG_DEFUALTS,
}

WEB_TYPES = {
	'port' : int,
	'debug': from_str_to_bool,
}

LOG_TYPES = {
	'loglevel': from_str_to_loglevel
}

TYPES = {
	'web': WEB_TYPES,
	'log': LOG_TYPES,
}

def parse_config(path, module):

	config = None
	with open(path, 'r') as config_file:
		config = json.load(config_file)

	if DEBUG:
		print('Configuration as loaded from file (file={}).'.format(path))
		print(config)
		print()

	config = config[module]

	if DEBUG:
		print('Configuration after selecting module (module={}).'.format(module))
		print(config)
		print()

	return config

def set_defaults(config, module):
	def set_default(dict, key, value):
		if key not in dict:
			dict[key] = value
		return dict

	for key, value in DEFAULTS[module].items():
		set_default(config, key, value)

	if DEBUG:
		print('Configuration after setting defaults.')
		print(config)
		print()

	return config

def enforce_datatypes(config, module):
	def enforce_datatype(dict, key, from_str_to_x):
		value           = dict[key]
		converted_value = from_str_to_x(value)
		dict[key]       = converted_value
		return dict

	for key, value in TYPES[module].items():
		enforce_datatype(config, key, value)

	if DEBUG:
		print('Configuration after enforcing types.')
		print(config)
		print()

	return config

def load_config(path, module):
	config = parse_config(path, module)
	config = set_defaults(config, module)
	config = enforce_datatypes(config, module)
	return config