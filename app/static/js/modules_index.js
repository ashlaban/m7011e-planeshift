var vm;

loadModulesData = function () {
	$.ajax({
		url: '/api/modules',
		// error: function() {
		// 	$('#info').html('<p>An error has occurred. Could not contact api.</p>');
		// },
		dataType: 'json',
		success: function(data) {
			// console.log("PlaneshiftViewModel -- loaded modules list", data);
			
			vm = new PlaneshiftViewModel(data.data);
			ko.applyBindings(vm);
			console.log(vm);
		},
		type: 'GET'
	});
}

function PlaneshiftViewModel(modulesData) {
	var self = this;

	self.modules = modulesData;
}

loadModulesData()