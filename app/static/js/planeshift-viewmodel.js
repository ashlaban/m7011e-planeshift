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
	this.current_module = ko.observable(generate_empty_plane());
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
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.plane_list(json.data);
	};

	planeshift.fetch.plane_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_plane_list_for_user = function (username) {
	var self = this;
	var data = {username: username};
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.plane_list(json.data);
	};

	planeshift.fetch.plane_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_plane = function (name) {
	var self = this;
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.current_plane(json.data);
	};

	planeshift.fetch.plane(name, success, error);
}

PlaneshiftViewModel.prototype.remove_plane = function (name, success, error) {
	console.log('Deleteing plane')
	var success = success || planeshift.redirect.to.module_list();
	var error   = error   || planeshift.error.default();
	
	planeshift.remove.plane(name, success, error);
}

PlaneshiftViewModel.prototype.enter_plane = function (name, success, error) {
	console.log('Deleteing plane')
	var success = success || planeshift.redirect.to.module_list();
	var error   = error   || planeshift.error.default();
	
	// planeshift.enter(name, success, error);
}

PlaneshiftViewModel.prototype.leave_plane = function (name, success, error) {
	console.log('Deleteing plane')
	var success = success || planeshift.redirect.to.module_list();
	var error   = error   || planeshift.error.default();
	
	// planeshift.leave(name, success, error);
}

// ========================================================================
// === FILES
// ========================================================================
PlaneshiftViewModel.prototype.add_file = function (file) {
	this.file_list.push(file);
}

PlaneshiftViewModel.prototype.add_files = function (files) {
	var length = files.length;
	for (var i = 0; i < length; ++i) {
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
	var error       = error   || planeshift.error.default();
	var success     = success || planeshift.redirect.to.module(module_name);

	console.log('Uploading.');
	planeshift.upload.files(module_name, form_data, success, error);
}

PlaneshiftViewModel.prototype.upload_files_from_form = function (form, success, error) {
	var version_name = form.version.value;
	this.upload_files(version_name);
}

// ========================================================================
// === MODULES
// ========================================================================
PlaneshiftViewModel.prototype.get_module_list = function (success, error) {
	var self = this;
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.module_list(json.data);
	};
	
	planeshift.fetch.module_list({}, success, error);
}

PlaneshiftViewModel.prototype.get_module_list_for_user = function (username, success, error) {
	var self = this;
	var data = {username: username};
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.module_list(json.data);
	};

	planeshift.fetch.module_list(data, success, error);
}

PlaneshiftViewModel.prototype.get_module = function (name, success, error) {
	var self = this;
	var error   = error   || planeshift.error.default;
	var success = success || function (json) {
		self.current_module(json.data);
	};
	
	planeshift.fetch.module(name, success, error);
}

PlaneshiftViewModel.prototype.create_module = function (name, short_desc, long_desc, success, error) {
	var error   = error   || planeshift.error.default();
	var success = success || planeshift.redirect.to.module(name);
	
	planeshift.create.module(name, short_desc, long_desc, success, error);
}

PlaneshiftViewModel.prototype.create_module_from_form = function (form, success, error) {
	var name       = form.name.value;
	var short_desc = form.short_desc.value;
	var long_desc  = form.long_desc.value;

	this.create_module(name, short_desc, long_desc);
}

PlaneshiftViewModel.prototype.remove_module = function (name, success, error) {
	console.log('Deleteing module')
	var success = success || planeshift.redirect.to.module_list();
	var error   = error   || planeshift.error.default();
	
	planeshift.remove.module(name, success, error);
}