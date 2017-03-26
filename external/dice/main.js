function dice(sides, n) {
	var sum = 0;
	for (var i = 0; i < n; ++i) {
		sum += Math.floor(Math.random()*sides) + 1;
	}

	return sum;
}

function DiceViewModel() {
	this.connected_users = ko.observable(CONNECTED_USERS);
	this.plane_name      = ko.observable(PLANE_NAME);
	this.current_user    = ko.observable(CURRENT_USER);

	this.n_dice = ko.observable(1);
	this.sides  = ko.observable(6);
	this.available_n      = [1,2,3,4,5,6,7,8,9,10];
	this.available_sides  = [2,3,6,8,12,20,100];

	this.latest_user = ko.observable('');
	this.latest_dice = ko.observable('');
	this.latest_val  = ko.observable(0);
	this.data   = ko.observable();
}

DiceViewModel.prototype.publish_dice = function () {
	var d = dice(this.sides(), this.n_dice());
	var s = ''+this.n_dice()+'d'+this.sides()
	console.log(d)
	set_user_data({val: d});
	set_data({latest: {val:d, dice:s, user:this.current_user()}});
}

DiceViewModel.prototype.get_latest = function () {
	var self = this;

	get_data(true, function(data) {
		console.log(data)
		self.latest_user(data['data']['latest']['user']);
		self.latest_dice(data['data']['latest']['dice']);
		self.latest_val(data['data']['latest']['val']);
		self.data(data['data'])
	});
}

var view_model = new DiceViewModel();	
document.addEventListener("DOMContentLoaded", function(event) {
	var userlist = document.getElementById('users');

	
	ko.applyBindings(view_model);
	view_model.get_latest()

	window.setInterval(function(){view_model.get_latest()}, 1500);
});
