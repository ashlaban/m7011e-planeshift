import json

def make_json_error(msg=''):
	response = {
		'status': 'error',
		'msg'   : msg,
	}
	return json.dumps(response)

def make_json_success(data=None, msg=''):
	response = {
			'status': 'ok',
			'msg'   : msg,
		}

	if data is not None:
		response['data'] = data

	return json.dumps(response)