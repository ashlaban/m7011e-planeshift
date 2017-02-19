
var generate_empty_model = function () {
	return {
		name          : "",
		picture       : "",
		short_desc    : "",
		long_desc     : "",
		is_owner      : false,
		owner         : "",
		versions      : [],
		latest_version: [],
	}
}

function PlaneshiftViewModel() {
	this.current_module = ko.observable(generate_empty_model());
	this.module_list    = ko.observableArray();
	this.file_list      = ko.observableArray();

	this.button_callback_map = {};
}
// ========================================================================
// === CLICK BUTTON CALLBACKS
// ========================================================================
PlaneshiftViewModel.prototype.add_button_callback = function (button_id, callback) {
	this.button_callback_map[button_id] = callback;
}

PlaneshiftViewModel.prototype.remove_button_callback = function (button_id) {
	delete this.button_callback_map[button_id];
}

PlaneshiftViewModel.prototype.clear_button_callbacks = function () {
	this.button_callback_map = {};
}

PlaneshiftViewModel.prototype.apply_button_callbacks = function () {
	for (var button_id in this.button_callback_map) {
		var button   = document.getElementById(button_id);
		var callback = this.button_callback_map[button_id];
		button.addEventListener('click', callback, false);
	}
}

// ========================================================================
// === FILES
// ========================================================================
PlaneshiftViewModel.prototype.add_file = function (file) {
	this.files.push(file);
}

PlaneshiftViewModel.prototype.add_files = function (files) {
	var length = files.length;
	for (var i = 0; i < length; ++i) {
		var file = files[i];
		this.addFile(file);
	}
}

PlaneshiftViewModel.prototype.clear_files = function () {
	this.files.removeAll();
}

PlaneshiftViewModel.prototype.remove_file = function (name) {
	for (var file of this.files()) {
		if (file.name === name) { return this.files.remove(file); }
	}
}

PlaneshiftViewModel.prototype.get_files_as_form_data = function () {
	form_data = new FormData();

	for (var file of this.files()) {
		console.log('Appending file ' + file.name + ' to form data.');
		form_data.append('files', file);
	}

	console.log('Appending version name ' + version_name + ' to form data.');
	form_data.append('version', version_name);

	console.log('Done constructing form data.');
	console.log(form_data);

	return form_data;
}

PlaneshiftViewModel.prototype.upload_files = function (version_name) {
	var form_data = this.get_files_as_form_data();
	var success   = planeshift.redirect.to_module(this.current_module.name);
	var error     = planeshift.error.default();

	console.log('Uploading.');
	planeshift.upload.files(form_data, success, error);
}

PlaneshiftViewModel.prototype.upload_files_from_form = function (form) {
	var version_name = form.version_name.value;
	this.upload_files(version_name);
}

// ========================================================================
// === MODULES
// ========================================================================
PlaneshiftViewModel.prototype.get_module_list = function () {
	var self = this;
	var error   = planeshift.error.default;
	var success = function (json) {
		self.module_list(json.data);
		self.apply_button_callbacks();
	};
	
	planeshift.fetch.module_list(success, error);
}

PlaneshiftViewModel.prototype.get_module = function (name) {
	var self = this;
	var error   = planeshift.error.default;
	var success = function (json) {
		self.current_module(json.data);
		self.apply_button_callbacks();
	};
	

	planeshift.fetch.module(name, success, error);
}

PlaneshiftViewModel.prototype.create_module = function (name, short_desc, long_desc) {
	var success = planeshift.redirect.to_module(name);
	var error   = planeshift.error.default();
	
	planeshift.create.module(name, short_desc, long_desc, success, error);
}

PlaneshiftViewModel.prototype.create_module_from_form = function (form) {
	var name       = form.name.value;
	var short_desc = form.short_desc.value;
	var long_desc  = form.long_desc.value;

	this.create_module(name, short_desc, long_desc);
}

PlaneshiftViewModel.prototype.remove_module = function (name) {
	console.log('Deleteing module')
	var success = planeshift.redirect.to_module_list();
	var error   = planeshift.error.default();
	
	planeshift.remove.module(name, success, error);
}