// Requires: jquery

var planeshift = (function () {

	// ========================================================================
	// === LOW LEVEL API
	// ========================================================================
	var api_get = function (url, data, success, error) {
		console.log('GET call to', url);
		error = error || default_error;
		$.ajax({
			type     : 'GET'  ,
			url      : url    ,
			data     : data,
			dataType : 'json' ,
			success  : success,
			error    : error  ,
		});
	}

	var api_post = function (url, data, success, error) {
		console.log('POST call to', url, data);
		error = error || default_error;
		$.ajax({
			type        : 'POST'  ,
			url         : url     ,
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
		error = error || default_error;
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
		error = error || default_error;
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

	var redirect_to_plane_list = function () {
		return redirect('/plane');
	}

	var redirect_to_plane = function (name) {
		return redirect('/planes/name/'+name);
	}

	var redirect_to_module_list = function () {
		return redirect('/modules');
	}

	var redirect_to_module = function (name) {
		return redirect('/modules/name/'+name);
	}

	var redirect_to_module_new_version = function (name) {
		return redirect('/modules/upload/'+name);
	}

	var redirect_to_profile = function () {
		return redirect('/profile');
	}

	var redirect_to_dashboard = function () {
		return redirect('/dashboard');
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

	function get_plane_list (data, success, error) {
		var url = '/api/planes';
		var data = data || {};
		api_get(url, data, success, error);
	}

	function get_plane (name, success, error) {
		var url = '/api/planes/'+name;
		var data = data || {};
		api_get(url, data, success, error);
	}

	function get_module_list (data, success, error) {
		var url = '/api/modules';
		var data = data || {};
		api_get(url, data, success, error);
	}

	function get_module (name, success, error) {
		var url = '/api/modules/'+name;
		var data = {};
		api_get(url, data, success, error);
	}

	function delete_module(name, success, error) {
		var data = {name: name};
		var url  = '/api/modules/';
		api_delete(url, data, success, error);
	}

	function create_module(name, short_desc, long_desc, success, error) {
		var url  = '/api/modules/'
		var data = {
			name       : name,
			short_desc : short_desc,
			long_desc  : long_desc,
		};
		
		api_post(url, data, success, error);
	}

	function upload_files(module_name, form_data, success, error) {
		var url   = "/api/modules/"+module_name;
		var data  = form_data;
		api_post_files(url, data, success, error);
	}

	// ========================================================================
	// === RETURN
	// ========================================================================

	return {
		// Low level api with signature fn(url, data, success, error)
		api: {
			get        : api_get,
			post       : api_post,
			post_files : api_post_files,
			delete     : api_delete,	
		},

		// Helpers for success and error callbacks.
		redirect: { to : {
			// to             : redirect,
			plane_list  : redirect_to_plane_list,
			plane       : redirect_to_plane,
			module_list : redirect_to_module_list,
			module      : redirect_to_module,
			module_new_version: redirect_to_module_new_version,
			profile     : redirect_to_profile,
			dashboard   : redirect_to_dashboard, // Not implemented yet
		}},
		error: {
			default: default_error,
		},

		// High level get and post requests. Uses the low level api internally.
		fetch: {
			plane_list: get_plane_list,
			plane     : get_plane,
			module_list: get_module_list,
			module     : get_module,
		},
		create: {
			module: create_module,
		},
		remove: {
			module: delete_module,
		},
		upload: {
			files: upload_files
		}
	}
})();