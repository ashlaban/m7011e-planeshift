// Requires: jquery

var planeshift = (function () {

	// ========================================================================
	// === LOW LEVEL API
	// ========================================================================
	var api_get = function (url, success, error) {
		console.log('GET call to', url);
		var wrapped_success = function (json) {
			console.log(json);
			success(json);
		};
		error = error | default_error;
		$.ajax({
			type     : 'GET'  ,
			url      : url    ,
			dataType : 'json' ,
			success  : wrapped_success,
			error    : error  ,
		});
	}

	var api_post = function (url, data, success, error) {
		console.log('POST call to', url, data);
		error = error | default_error;
		$.ajax({
			type        : 'POST'  ,
			url         : url    ,
			data        : JSON.stringify(data),
			dataType    : 'json',
			processData : false,
			contentType : 'application/json; charset=utf-8',
			success     : success,
			error       : error  ,
		});
	}

	var api_post_files = function (url, data, success, error) {
		console.log('POST (file) call to', url, data);
		error = error | default_error;
		$.ajax({
			type        : 'POST' ,
			url         : url    ,
			data        : data   ,
			processData : false  ,
			contentType : false  ,
			success     : success,
			error       : error  ,
		});
	}

	var api_delete = function (url, data, success, error) {
		console.log('DELETE call to', url, data);
		// error = error | default_error;
		$.ajax({
			type        : 'DELETE'  ,
			url         : url    ,
			data        : JSON.stringify(data),
			dataType    : 'json',
			processData : false,
			contentType : 'application/json; charset=utf-8',
			success     : success,
			error       : error  ,
		});
	}

	// ========================================================================
	// === REDIRECT
	// ========================================================================
	var redirect = function (url) {
		return function () { window.location = url; };
	}

	var redirect_to_module_list = function () {
		return redirect('/modules');
	}

	var redirect_to_module = function (name) {
		return redirect('/modules/name/'+name);
	}

	var default_error = function () {
		return function (response) {
			console.log('Error message', response)
			$('#info').html(response.responseJSON.msg);
		};
	}

	// ========================================================================
	// === HIGH LEVEL API
	// ========================================================================

	function get_module_list (success, error) {
		api_get('/api/modules', success, error)
	}

	function get_module_info (name, success, error) {
		api_get('/api/modules/'+name, success, error);
	}

	function delete_module(name, success, error) {
		var data = {name: name};
		var url  = '/api/modules/';
		api_delete(url, data, success, error);
	}
	function create_module(name, short_desc, long_desc) {
		var url  = '/api/modules/'
		var data = {
			name: name,
			short_desc: short_desc,
			long_desc: long_desc,
		};
		
		api_post(url, data, success, error);
	}

	function uploadFiles(form_data, success, error) {
		var url   = "/api/modules/{{module_name}}";
		var data  = form_data;
		api_post_files(url, data, success, error);
	}

	// ========================================================================
	// === RETURN
	// ========================================================================

	return {
		// Low level api with signature fn(url, data, success, error)
		// (Get lacks data).
		api: {
			get        : api_get,
			post       : api_post,
			post_files : api_post_files,
			delete     : api_delete,	
		},

		// Helpers for success and error callbacks.
		redirect: {
			to             : redirect,
			to_module_list : redirect_to_module_list,
			to_module      : redirect_to_module,
		},
		error: {
			default: default_error,
		},

		// High level get and post requests. Uses the low level api internally.
		fetch: {
			module_list: get_module_list,
			module     : get_module_info,
		},
		create: {
			module: create_module,
		},
		remove: {
			module: delete_module,
		},
		upload: {
			files: uploadFiles
		}
	}
})();