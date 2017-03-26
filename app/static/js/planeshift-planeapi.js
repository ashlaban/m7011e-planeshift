
/**
 * Convenience function for interaction with user private data.
 */
function set_user_data(data, success, error) {
	_ = {}
	_[CURRENT_USER] = data
	_set_data(PLANE_NAME, _, success, error);
}

/**
 * Convenience function for interaction with user private data.
 */
function get_user_data(key, success, error) {
	_ = {}
	_[CURRENT_USER] = key
	_get_data(PLANE_NAME, _, success, error);
}

/**
 * Convenience function. Uses the automatically set global variable PLANE_NAME 
 * to simplify function signature.
 */
function set_data(data, success, error) {
	_set_data(PLANE_NAME, data, success, error);
}

/**
 * Convenience function. Uses the automatically set global variable PLANE_NAME 
 * to simplify function signature.
 */
function get_data(key, success, error) {
	_get_data(PLANE_NAME, key, success, error);
}

/**
 * Sets data in the plane store.
 * 
 * @param {[type]} plane_name [description]
 * @param {[type]} key        [description]
 * @param {[type]} value      [description]
 * @param {[type]} success    [description]
 * @param {[type]} error      [description]
 */
function _set_data(plane_name, data, success, error) {
	console.log('SENDING TO SERVER', data);

	$.ajax({
		type: 'POST',
		url: '/api/planes/'+plane_name+'/data',
		data: JSON.stringify({data: data}),
		dataType: 'json',
		processData: false,
		contentType: 'application/json; charset=utf-8',
		success: success,
		error  : error  ,
	});
}

/**
 * Gets data from the plane store.
 * 
 * @param  {[type]} plane_name [description]
 * @param  {[type]} key        [description]
 * @param  {[type]} success    [description]
 * @param  {[type]} error      [description]
 * @return {[type]}            [description]
 */
function _get_data(plane_name, key, success, error) {
	success = success || function(a){console.log(a);}
	error   = error   || function(a){console.log(a);}

	$.ajax({
		type: 'GET',
		url: '/api/planes/'+plane_name+'/data',
		data: 'key='+JSON.stringify(key),
		dataType: 'json',
		processData: false,
		contentType: 'application/json; charset=utf-8',
		success: success,
		error  : error  ,
	});
}