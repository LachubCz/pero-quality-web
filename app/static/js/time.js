var x;

start();

function start() {
    x = setInterval(timer, 10);
}

function stop() {
    clearInterval(x);
}

var milisec = 0;
var sec = 0;
var min = 0;
var hour = 0;

var miliSecOut = 0;
var secOut = 0;
var minOut = 0;
var hourOut = 0;

function timer() {
    miliSecOut = checkTime(milisec);
    secOut = checkTime(sec);
    minOut = checkTime(min);
    hourOut = checkTime(hour);

    milisec = ++milisec;

    if (milisec === 100) {
        milisec = 0;
        sec = ++sec;
    }

    if (sec == 60) {
        min = ++min;
        sec = 0;
    }

    if (min == 60) {
        min = 0;
        hour = ++hour;

    }

    document.getElementById("milisec").value = miliSecOut;
    document.getElementById("sec").value = secOut;
    document.getElementById("min").value = minOut;
    document.getElementById("hour").value = hourOut;
}

function checkTime(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}
