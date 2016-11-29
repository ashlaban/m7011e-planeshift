import logging

import rc

CONFIG_MODULE = 'log'

config = rc.load_config(path=rc.CONFIG_PATH, module=CONFIG_MODULE)

logging.basicConfig(
		filename=config['logfile'],
		level=config['loglevel'],
		format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
	)