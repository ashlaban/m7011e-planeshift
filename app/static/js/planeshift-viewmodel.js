var generate_empty_plane = function () {
	return {
		is_owner       : '',
		has_password   : false,
		module_name    : '',
		module_version : '',
		picture        : '',
		name           : '',
		public         : false,
		users          : [],
	}
}

var generate_empty_model = function () {
	return {
		name          : '',
		picture       : '',
		short_desc    : '',
		long_desc     : '',
		is_owner      : false,
		owner         : '',
		versions      : [],
		latest_version: [],
	}
}

function PlaneshiftViewModel() {
	this.current_module = ko.observable(generate_empty_model());
	this.current_plane  = ko.observable(generate_empty_plane());
	this.plane_list     = ko.observableArray();
	this.module_list    = ko.observableArray();
	this.file_list      = ko.observableArray();
}

// ========================================================================
// === PLANES
// ========================================================================
PlaneshiftViewModel.prototype.get_plane_list = function () {
	var self = this;
	var data = {};
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		var planes = json.data;
		planes.sort(function(a, b) {
			var x = a.name.toLowerCase(), y = b.name.toLowerCase();
			return x < y ? -1 : x > y ? 1 : 0;
		});
		self.plane_list(planes);
	};

	planeshift.fetch.plane_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_plane_list_for_user = function (username) {
	var self = this;
	var data = {username: username};
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		var planes = json.data;
		planes.sort(function(a, b) {
			var x = a.name.toLowerCase(), y = b.name.toLowerCase();
			return x < y ? -1 : x > y ? 1 : 0;
		});
		self.plane_list(planes);
	};

	planeshift.fetch.plane_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_plane = function (name) {
	var self = this;
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		self.current_plane(json.data);
	};

	planeshift.fetch.plane(name, success, error);
}

PlaneshiftViewModel.prototype.create_plane = function (data, success, error) {
	var success = success || planeshift.callback.redirect.to.plane(data.name);
	var error   = error   || planeshift.callback.error.default();

	planeshift.create.plane(data, success, error);
}

PlaneshiftViewModel.prototype.create_plane_from_form = function (form, success, error) {
	var data = {
		name     : form.name.value,
		password : form.password.value,
		module   : form.module.value,
		hidden   : form.hidden.checked,
	};
	
	this.create_plane(data, success, error);
}

PlaneshiftViewModel.prototype.remove_plane = function (name, success, error) {
	console.log('Deleting plane')
	var success = success || planeshift.callback.redirect.to.module_list();
	var error   = error   || planeshift.callback.error.default();
	
	planeshift.remove.plane(name, success, error);
}

PlaneshiftViewModel.prototype.enter_plane = function (name, success, error) {
	console.log('Deleting plane')
	var success = success || planeshift.callback.redirect.to.module_list();
	var error   = error   || planeshift.callback.error.default();
	
	// planeshift.enter(name, success, error);
}

PlaneshiftViewModel.prototype.leave_plane = function (name, success, error) {
	console.log('Deleting plane')
	var success = success || planeshift.callback.redirect.to.module_list();
	var error   = error   || planeshift.callback.error.default();
	
	// planeshift.leave(name, success, error);
}

// ========================================================================
// === FILES
// ========================================================================
PlaneshiftViewModel.prototype.contains_file = function (file) {
	for (var list_file of this.file_list()) {
		if (list_file.name === file.name) {return true;}
	}
	return false;
}

PlaneshiftViewModel.prototype.add_file = function (file) {
	if (! this.contains_file(file)) {
		this.file_list.push(file);
	}
}

PlaneshiftViewModel.prototype.add_files = function (files) {
	for (var i = 0; i < files.length; ++i) {
		var file = files[i];
		this.add_file(file);
	}
}

PlaneshiftViewModel.prototype.clear_files = function () {
	this.file_list.removeAll();
}

PlaneshiftViewModel.prototype.remove_file = function (name) {
	for (var file of this.file_list()) {
		if (file.name === name) { return this.file_list.remove(file); }
	}
}

PlaneshiftViewModel.prototype.get_files_as_form_data = function (version_name) {
	form_data = new FormData();

	for (var file of this.file_list()) {
		console.log('Appending file ' + file.name + ' to form data.');
		form_data.append('files', file);
	}

	console.log('Appending version name ' + version_name + ' to form data.');
	form_data.append('version', version_name);

	console.log('Done constructing form data.');
	console.log(form_data);

	return form_data;
}

PlaneshiftViewModel.prototype.upload_files = function (version_name, success, error) {
	var module_name = this.current_module().name;
	var form_data   = this.get_files_as_form_data(version_name);
	var error       = error   || planeshift.callback.error.default();
	var success     = success || planeshift.callback.redirect.to.module(module_name);

	console.log('Uploading.');
	planeshift.upload.files(module_name, form_data, success, error);
}

PlaneshiftViewModel.prototype.upload_files_from_form = function (form, success, error) {
	var version_name = form.version.value;
	this.upload_files(version_name, success, error);
}

// ========================================================================
// === MODULES
// ========================================================================
PlaneshiftViewModel.prototype.get_module_list = function (success, error) {
	var self = this;
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		var modules = json.data;
		modules.sort(function(a, b) {
			var x = a.name.toLowerCase(), y = b.name.toLowerCase();
			return x < y ? -1 : x > y ? 1 : 0;
		});
		self.module_list(modules);
	};
	
	planeshift.fetch.module_list({}, success, error);
}

PlaneshiftViewModel.prototype.get_module_list_for_user = function (username, success, error) {
	var self = this;
	var data = {username: username};
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		var modules = json.data;
		modules.sort(function(a, b) {
			var x = a.name.toLowerCase(), y = b.name.toLowerCase();
			return x < y ? -1 : x > y ? 1 : 0;
		});
		self.module_list(modules);
	};

	planeshift.fetch.module_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_module = function (name, success, error) {
	var self = this;
	var error   = error   || planeshift.callback.error.default();
	var success = success || function (json) {
		self.current_module(json.data);
	};
	
	planeshift.fetch.module(name, success, error);
}

PlaneshiftViewModel.prototype.create_module = function (name, success, error) {
	var error   = error   || planeshift.callback.error.default();
	var success = success || planeshift.callback.redirect.to.module(name);
	
	planeshift.create.module(name, success, error);
}

PlaneshiftViewModel.prototype.create_module_from_form = function (form, success, error) {
	var name       = form.name.value;

	this.create_module(name, success, error);
}

PlaneshiftViewModel.prototype.remove_module = function (name, success, error) {
	console.log('Deleting module')
	var success = success || planeshift.callback.redirect.to.module_list();
	var error   = error   || planeshift.callback.error.default();
	
	planeshift.remove.module(name, success, error);
}