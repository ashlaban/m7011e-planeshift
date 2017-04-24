#!/usr/bin/env python3
#
#

from flask import Flask
from flask_hookserver import Hooks

import re
import os
import subprocess

def redeploy_webserver(name, path, branch):
	'''Redeploy a webserver based in a git repo.
	'''
	
	print('Redeploying {name} web server (branch={branch}).'.format(name=name, branch=branch), '\n'*2)

	cwd = os.getcwd()
	os.chdir(path)


	print('Running command: ' + ' '.join(['sudo', 'systemctl', 'stop', name]), '\n'*2)
	subprocess.run(['sudo', 'systemctl', 'stop', name])
	
	print('Running command: ' + ' '.join(['git', 'stash']), '\n'*2)
	subprocess.run(['git', 'stash'])
	print('Running command: ' + ' '.join(['git', 'pull', 'origin', branch]), '\n'*2)
	subprocess.run(['git', 'pull', 'origin', branch])
	print('Running command: ' + ' '.join(['git', 'stash', 'pop']), '\n'*2)
	subprocess.run(['git', 'stash', 'pop'])

	# The two lines below is replacement for the above, and handles local changes better
	# print('Running command: ' + ' '.join(['git', 'fetch', 'origin', branch]), '\n'*2)
	# subprocess.run(['git', 'fetch', 'origin', branch])
	# print('Running command: ' + ' '.join(['git', 'merge', '-s', 'recursive', '-X', 'theirs', 'origin/{}'.format(branch)]), '\n'*2)
	# subprocess.run(['git', 'merge', '-s', 'recursive', '-X', 'theirs', 'origin/{}'.format(branch)])
	
	print('Running command: ' + ' '.join(['git', 'checkout', branch]), '\n'*2)
	subprocess.run(['git', 'checkout', branch])

	# Recreate the database and ensure permissions
	print('Running command: ' + ' '.join(['rm', 'app.db']), '\n'*2)
	subprocess.run(['rm', 'app.db'])
	print('Running command: ' + ' '.join(['./db_create.py']), '\n'*2)
	subprocess.run(['./db_create.py']) 
	print('Running command: ' + ' '.join(['./db_init.py']), '\n'*2)
	subprocess.run(['./db_init.py'])
	print('Running command: ' + ' '.join(['chmod', 'g+w', 'app.db']), '\n'*2)
	subprocess.run(['chmod', 'g+w', 'app.db'])

	print('Running command: ' + ' '.join(['sudo', 'systemctl', 'start', name]), '\n'*2)
	subprocess.run(['sudo', 'systemctl', 'start', name])

	os.chdir(cwd)
	return

app = Flask(__name__)
app.config['VALIDATE_IP']         = True
app.config['VALIDATE_SIGNATURE']  = True
app.config['GITHUB_WEBHOOKS_KEY'] = fill in the correct value here

hooks = Hooks(app, url='/hooks')

@hooks.hook('ping')
def ping(data, guid):
	print('Received: {}'.format(data), '\n'*2)
	return 'pong'

@hooks.hook('push')
def push(data, guid):
	#print('Received:\n{}'.format(data))
	#print('Guid: {}'.format(guid))

	if 'ref' not in data:
		print('Error: Did not find ref in push message.')
		return ':('
	ref_str       = data['ref']

	ref = re.match('refs/heads/(.*)', ref_str)
	if ref is None:
		print('Error: Do not understand what branch was pushed. Ref: {}'.format(ref_str))
		return ':('
	branch = ref.group(1)

	# Pushing to master means redeploy development server.
	# Pushing to 'prod' means redeploy production server.
	if branch == 'prod':
		service_path = '/var/local/www/m7011e/prod'
		service_name = 'planeshift-prod'
	elif branch == 'master':
		service_path = '/var/local/www/m7011e/dev'
		service_name = 'planeshift-dev'

	redeploy_webserver(service_name, service_path, branch)
	return 'OK!'

app.run(host='0.0.0.0', port=8999)
