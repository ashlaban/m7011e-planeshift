var data = {
	stone: 0,
	wheat: 0,
	brick: 0,
	wood : 0,
	sheep: 0,
}

function mod(amt, type) {
	if (data[type] + amt < 0) {
		return;
	}

	data[type] += amt;
	document.getElementById(type).innerHTML = data[type];

	set_user_data(data);
}

document.addEventListener("DOMContentLoaded", function(event) {

	document.getElementById("stone").innerHTML = 0;
	document.getElementById("wheat").innerHTML = 0;
	document.getElementById("brick").innerHTML = 0;
	document.getElementById("wood").innerHTML  = 0;
	document.getElementById("sheep").innerHTML = 0;


	get_user_data(true, function (d) {
		console.log(d)
		if (d.data.data[CURRENT_USER]) {
			data = d.data.data[CURRENT_USER];
			console.log(data)
		}
		
		if (data) {
			document.getElementById("stone").innerHTML = data.stone;
			document.getElementById("wheat").innerHTML = data.wheat;
			document.getElementById("brick").innerHTML = data.brick;
			document.getElementById("wood").innerHTML  = data.wood;
			document.getElementById("sheep").innerHTML = data.sheep;
		}
	});
});
