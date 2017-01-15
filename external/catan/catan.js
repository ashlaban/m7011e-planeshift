var stone;
var wheat;
var brick;
var wood;
var sheep;

stone = 0;
wheat = 0;
brick = 0;
wood = 0;
sheep = 0;

document.getElementById("stoneNum").innerHTML = stone;
document.getElementById("wheatNum").innerHTML = wheat;
document.getElementById("brickNum").innerHTML = brick;
document.getElementById("woodNum").innerHTML = wood;
document.getElementById("sheepNum").innerHTML = sheep;

function addStone(){
	stone = stone+1;
	document.getElementById("stoneNum").innerHTML = stone;
}
function subStone(){
	stone = stone-1;
	document.getElementById("stoneNum").innerHTML = stone;
}

function addWheat(){
	wheat = wheat+1;
	document.getElementById("wheatNum").innerHTML = wheat;
}
function subWheat(){
	wheat = wheat-1;
	document.getElementById("wheatNum").innerHTML = wheat;
}

function addBrick(){
	brick = brick+1;
	document.getElementById("brickNum").innerHTML = brick;
}
function subBrick(){
	brick = brick-1;
	document.getElementById("brickNum").innerHTML = brick;
}

function addWood(){
	wood = wood+1;
	document.getElementById("woodNum").innerHTML = wood;
}
function subWood(){
	wood = wood-1;
	document.getElementById("woodNum").innerHTML = wood;
}

function addSheep(){
	sheep = sheep+1;
	document.getElementById("sheepNum").innerHTML = sheep;
}
function subSheep(){
	sheep = sheep-1;
	document.getElementById("sheepNum").innerHTML = sheep;
}
