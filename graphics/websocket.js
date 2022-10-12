//var output = document.getElementById('serveroutput');
var isMouseDown = false;

addEventListener("mousedown", function() {
    isMouseDown = true;
});

addEventListener("mouseup", function() {
    isMouseDown = false;
});

var s = new WebSocket("ws://localhost:8889");
var n = false;
var p = '';
var showFramesSelector = false;

s.onopen = function(e) {
//  sendMsg(300);
//	out('connected');
//	var d = JSON.parse(e.data);
}

s.onerror = function(e) {
	alert(e);
}

s.onclose = function(e) {
	if (event.wasClean) {
		out("WS: " + `[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
	} else {
		out("WS: " + `[close] Connection died, code=${event.code} reason=${event.reason}`);
	}
}

s.onmessage = function(e) {
    if(document.getElementById('s1').checked) {
        if (typeof(e) !== 'undefined') {
            try {
                console.log(e.data);
                var d = JSON.parse(e.data);
                var trace = doTrace(d);
                var layout = doLayout(d.pair);

                updTitle(d.pair + ' ' + d.time);

                if (!showFramesSelector) {
                    renderFramesSelector(d.frames);
                    showFramesSelector = true;
                }

                if (!n) {
                    layout.uirevision = false;
                    Plotly.newPlot('graph', trace, layout, config);
                    n = true;
                    p = d.pair;
                } else {
                    if (!isMouseDown) {
                        Plotly.react('graph', trace, layout, config);
                    }
                    p = d.pair;
                }
            } catch (err) {
                console.log(err);
            }
        }
    }
}

function sendMsg(msg) {
	s.send(JSON.stringify({
        display_timeframe: msg,
    }));
}

function out(text) {
	var el = document.createElement('p');
	el.innerHTML = text;
	document.querySelector('body').appendChild(el);
}

function updTitle(text) {
    document.getElementById('time').innerHTML = text;
}

function resetZoom() {
    // сбрасываем масштаб при переходе на другой таймфрейм
    n = false;
}

function renderFramesSelector(frames) {
    for(let frame in frames) {
        var check = (frames[frame] == '5m') ? 'checked' : '';
        var code = '<input ' + check + ' type="radio" id="' + frames[frame] + '" name="tframe" onclick="sendMsg(id);resetZoom();"><label for="' + frames[frame] + '">' + frames[frame] + '</label>';
        document.getElementById('inputs').innerHTML += code;
    }
}
