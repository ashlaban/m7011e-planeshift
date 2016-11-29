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

import logging
import rc
import log

from app import app

CONFIG_MODULE = 'web'
rc.DEBUG      = True

def start():
	run_logger = logging.getLogger('runner')

	run_logger.info('Loading configuration.')
	config = rc.load_config(path=rc.CONFIG_PATH, module=CONFIG_MODULE)
	
	run_logger.info('Starting server')
	app.run(**config)

if __name__ == '__main__':
	start()

