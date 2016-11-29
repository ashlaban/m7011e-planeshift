#!/usr/bin/env python3
#
# Script to start the planeshift web application.
# Invoke as ./run and make sure you specified a config.json for runtime
# configuration. Format for config file is json dict. The parsed dict will be 
# passed to the application entry-point (app.run) and thus expects arguments the
# same as for that function.
# 
# There are a few default values, check out the corresponding function for
# details.
# 
# Note that only strings can be specified. But e.g. the debug parameter should 
# be a boolean. Thus type coercion is performed for a few known parameters.
#

import json

from app import app

CONFIG_PATH = './config.json'
DEBUG = True

def from_str_to_bool(x):
	if type(x) is not str:
		raise ValueError('Input data ({}) is not string.'.format(x))

	if x == "True" or x == "true":
		return True

	if x == "False" or x == "false":
		return False

	raise ValueError('Value cannot be conveted to bool. "{}" is not "True" or "False".'.format(x))
	return

def parse_config(path):

	config = None
	with open(path, 'r') as config_file:
		config = json.load(config_file)

	if DEBUG:
		print('Configuration as loaded from file (file={}).'.format(path))
		print(config)
		print()

	return config

def set_defaults(config):
	def set_default(dict, key, value):
		if key not in dict:
			dict[key] = value
		return dict

	set_default(config, 'host', '0.0.0.0')
	set_default(config, 'port', '8081')
	set_default(config, 'debug', 'False')

	if DEBUG:
		print('Configuration after setting defaults.')
		print(config)
		print()

	return config

def enforce_datatypes(config):
	def enforce_datatype(dict, key, from_str_to_x):
		value           = dict[key]
		converted_value = from_str_to_x(value)
		dict[key]       = converted_value
		return dict

	enforce_datatype(config, 'debug', from_str_to_bool)

	if DEBUG:
		print('Configuration after enforcing types.')
		print(config)
		print()

	return config

def load_config(path):
	config = parse_config(path)
	config = set_defaults(config)
	config = enforce_datatypes(config)
	return config

def start():
	config = load_config(CONFIG_PATH)
	app.run(**config)

if __name__ == '__main__':
	start()

