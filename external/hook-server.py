#!/usr/bin/env python3
#
#

from flask import Flask
from flask_hookserver import Hooks

import re
import os
import subprocess

def redeploy_webserver(path, branch):
	'''Redeploy a webserver based in a git repo.
	'''
	
	print('Redeploying {branch} web server'.format(branch=branch))

	cwd = os.getcwd()
	os.chdir(path)

	subprocess.run(['sudo', 'systemctl', 'stop', 'planeshift-'+branch])
	
	subprocess.run(['git', 'stash'])
	subprocess.run(['git', 'pull', 'origin', branch])
	subprocess.run(['git', 'stash', 'pop'])

	# The two lines below is replacement for the above, and handles local changes better
	# subprocess.run(['git', 'fetch', 'origin', branch])
	# subprocess.run(['git', 'merge', '-s', 'recursive', '-X', 'theirs', 'origin/{}'.format(branch)])
	
	subprocess.run(['git', 'checkout', branch])

	# Recreate the database and ensure permissions
	subprocess.run(['rm', 'app.db'])
	subprocess.run(['./db_create.py']) 
	subprocess.run(['./db_init.py'])
	subprocess.run(['chmod', 'g+w', 'app.db'])

	subprocess.run(['sudo', 'systemctl', 'start', 'planeshift-'+branch])

	os.chdir(cwd)
	return

app = Flask(__name__)
app.config['VALIDATE_IP']         = True
app.config['VALIDATE_SIGNATURE']  = True
app.config['GITHUB_WEBHOOKS_KEY'] = fill in the correct value here

hooks = Hooks(app, url='/hooks')

@hooks.hook('ping')
def ping(data, guid):
	print('Received: {}'.format(data))
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
		path = '/var/local/www/m7011e/prod'
	elif branch == 'master':
		path = '/var/local/www/m7011e/dev'

	redeploy_webserver(path, branch)
	return 'OK!'

app.run(host='0.0.0.0', port=8999)
