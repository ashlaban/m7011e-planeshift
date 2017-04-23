var g_data = {
	stone: 0,
	wheat: 0,
	brick: 0,
	wood : 0,
	sheep: 0,
}

function mod(amt, type) {
	if (g_data[type] + amt < 0) {
		return;
	}

	g_data[type] += amt;
	document.getElementById(type).innerHTML = g_data[type];

	set_user_data(g_data);
}

document.addEventListener("DOMContentLoaded", function(event) {

	document.getElementById("stone").innerHTML = 0;
	document.getElementById("wheat").innerHTML = 0;
	document.getElementById("brick").innerHTML = 0;
	document.getElementById("wood").innerHTML  = 0;
	document.getElementById("sheep").innerHTML = 0;


	get_user_data(true, function (data) {
		if (data[CURRENT_USER]) {
			g_data = data[CURRENT_USER];
			console.log(g_data)
		}
		
		if (g_data) {
			document.getElementById("stone").innerHTML = g_data.stone;
			document.getElementById("wheat").innerHTML = g_data.wheat;
			document.getElementById("brick").innerHTML = g_data.brick;
			document.getElementById("wood").innerHTML  = g_data.wood;
			document.getElementById("sheep").innerHTML = g_data.sheep;
		}
	});
});
