var data = {
	stone: 0,
	wheat: 0,
	brick: 0,
	wood : 0,
	sheep: 0,
}

function mod(amt, type, user, plane_name) {
	data[type]+= amt;
	document.getElementById(type).innerHTML = data[type];

	$.ajax({
			type: 'POST',
			url: '/api/planes/'+plane_name+'/data',
			data: JSON.stringify(data),
			dataType: 'json',
			processData: false,
			contentType: 'application/json; charset=utf-8',
		});
}

document.addEventListener("DOMContentLoaded", function(event) {
	$.ajax({
			type: 'GET',
			url: '/api/planes/'+plane_name,
			dataType: 'json',
			processData: false,
			contentType: 'application/json; charset=utf-8',
			success: function (d) {
				console.log(d)
				data = d.;
				document.getElementById("stone").innerHTML = data.stone;
				document.getElementById("wheat").innerHTML = data.wheat;
				document.getElementById("brick").innerHTML = data.brick;
				document.getElementById("wood").innerHTML  = data.wood;
				document.getElementById("sheep").innerHTML = data.sheep;
			},
		});	
});
