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

def parse_request_to_json(req):
	args = req.get_json()
	args = collections.defaultdict(lambda:None, **args) if args is not None else collections.defaultdict(lambda:None)
	return args

def html_escape_or_none(item)
	return werkzeug.utils.escape(item) if item is not None else None