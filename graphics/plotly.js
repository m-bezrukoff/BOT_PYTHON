
function doTrace(d) {
    var traces = [];

	traces.push({
		type: 'candlestick',
//		type: 'ohlc',
		name: '',
		open: d.open,
		close: d.close,
		high: d.high,
		low: d.low,
		x: d.date,
		decreasing: {line: {color: '#ff0000'}},
		increasing: {line: {color: '#00B519'}},
		opacity: 0.4,
		showlegend: false,
		annotations: [],
		text: d.amplitude,
	});

// ------------------------------------------------- TEST HERE ------------------------------------------------------------
//    if (d.vortex.dif) {
//        var index;
//        var v_x = []
//        var v_y = []
//        for (index = 0; index < d.vortex.dif.length; ++index) {
//            if (d.vortex.pos[index] > 1.23) {
//                v_x.push(d.date[index]);
//                v_y.push(d.high[index]);
//            }
//        }
//        traces.push({
//            type: 'scatter',
//            name: 'Vortex IN',
//            y: v_y,
//            x: v_x,
//            marker: {'size': 10, 'color': 'yellow', 'symbol': 1},
//            mode: 'markers',
//            showlegend: false,
//        });
//    }
// ------------------------------------------------- TEST HERE ------------------------------------------------------------

    if (d.peaks) {
        traces.push({
            type: 'scatter',
            name: 'Peaks',
            y: d.peaks.peaks.y,
            x: d.peaks.peaks.x,
            marker: {'size': 8, 'color': '#fff', 'symbol': 6},
            mode: 'markers',
            showlegend: false,
        });
        traces.push({
            type: 'scatter',
            name: 'Peaks',
            y: d.peaks.troughs.y,
            x: d.peaks.troughs.x,
            marker: {'size': 8, 'color': '#fff', 'symbol': 5},
            mode: 'markers',
            showlegend: false,
        });
    }

    traces.push({
        type: 'scatter',
        name: 'clustets',
        marker: {'size': d.clusters.size, 'color': d.clusters.color, 'line': {'width': 1.5}},
        x: d.clusters.x,
        y: d.clusters.y,
        mode: 'markers',
        opacity: 0.8,
        showlegend: false,
    });

    traces.push({
		type: 'scatter',
		name: 'TMA fast',
		y: d.tma_f,
		x: d.date,
		opacity: 0.99,
		line: {color: 'red', width: 2},
		mode: 'lines',
		showlegend: false,
	});

    traces.push({
		type: 'scatter',
		name: 'TMA medium',
		y: d.tma_m,
		x: d.date,
		opacity: 0.99,
		line: {color: '#fff', width: 2},
		mode: 'lines',
		showlegend: false,
	});

//	traces.push({
//		type: 'scatter',
//		name: 'TMA slow',
//		y: d.tma_s,
//		x: d.date,
//		opacity: 0.99,
//		line: {color: 'yellow', width: 1.5},
//		mode: 'lines',
//		showlegend: false,
//	});

    if (d.rate != 0) {
        traces.push({
            type: 'line',
            name: 'Rate',
            y: [d.rate, d.rate],
            x: [d.date[0], d.date[d.date.length - 1]],
            line: {color: '#fff', width: 1.5},
            mode: 'lines',
            showlegend: false,
        });
    }

    if (d.bid != 0) {
        traces.push({
            type: 'scatter',
            name: 'Bid',
            y: [d.bid, d.bid],
            x: [d.date[0], d.date[d.date.length - 1]],
            line: {color: '#ff0000', width: 0.9, dash:'dot'},
            mode: 'lines',
            showlegend: false,
        });
    }

    if (d.ask != 0) {
        traces.push({
            type: 'scatter',
            name: 'Ask',
            y: [d.ask, d.ask],
            x: [d.date[0], d.date[d.date.length - 1]],
            line: {color: '#00B519', width: 0.9, dash:'dot'},
            mode: 'lines',
            showlegend: false,
        });
    }

	traces.push({
		type: 'bar',
		name: 'MACD',
		y: d.macd_h,
		x: d.date,
		yaxis: 'y2',
		marker: {color: d.macd_c, line: {width: 0}},
		opacity: 0.5,
		showlegend: false,
	});
//    traces.push({
//		type: 'scatter',
//		name: 'Vortex neg',
//		y: d.vortex.neg,
//		x: d.date,
//		yaxis: 'y2',
//		line: {color: 'red', width: 1.5},
//		mode: 'lines',
//		showlegend: false,
//	});
//
//    traces.push({
//		type: 'scatter',
//		name: 'Vortex pos',
//		y: d.vortex.pos,
//		x: d.date,
//		yaxis: 'y2',
//		line: {color: 'green', width: 1.5},
//		mode: 'lines',
//		showlegend: false,
//	});
//
//    traces.push({
//		type: 'bar',
//		name: 'Vortex dif',
//		y: d.vortex.dif,
//		x: d.date,
//		yaxis: 'y4',
//		opacity: 0.5,
//		showlegend: false,
//	});

//	traces.push({
//		type: 'bar',
//		name: 'EMA DIFF',
//		y: d.ema_diff,
//		x: d.date,
//		yaxis: 'y2',
//		marker: {color: d.ema_diff_c, line: {width: 0}},
//		opacity: 0.5,
//		showlegend: false,
//	});

	traces.push({
		type: 'bar',
		name: 'Volume',
		y: d.volume,
		x: d.date,
		yaxis: 'y3',
		opacity: 0.5,
		marker: {color: '#00B519', line: {width: 0}},
		showlegend: false,
	});

    if (d.trade_points) {
        traces.push({
            type: 'scatter',
            name: 'Open points',
            y: d.trade_points.open.y,
            x: d.trade_points.open.x,
            marker: {'size': 8, 'color': '#8aff00', 'symbol': d.trade_points.open.marker, 'line': {'color': '#fff', 'width': 1.2}},
            mode: 'markers',
            showlegend: false,
        });

        traces.push({
            type: 'scatter',
            name: 'Close points',
            y: d.trade_points.close.y,
            x: d.trade_points.close.x,
            marker: {'size': 8, 'color': 'red', 'symbol': d.trade_points.open.marker, 'line': {'color': '#fff', 'width': 1.2}},
            mode: 'markers',
            showlegend: false,
        });
    }

//    if (d.convergence_points) {
//        traces.push({
//            type: 'scatter',
//            name: 'Convergence',
//            y: d.convergence_points.y,
//            x: d.convergence_points.x,
//            marker: {'size': 3, 'color': '#fff', 'symbol': 0, 'line': {'color': '#fff', 'width': 1.2}},
//            mode: 'markers',
//            showlegend: false,
//        });
//    }
    return traces;
}

function doLayout(t) {
	return {
	    uirevision: true,
		dragmode: 'pan',
		hovermode: 'x unified',
		hoverlabel: {font: {color: '#ccc'}},

		legend: {
			font: {color: '#ccc'},
			orientation: 'h',
			x: 0.01,
			y: 0.99,
			yanchor: 'top'
		},

		paper_bgcolor: '#1e1e1e',
		plot_bgcolor: '#222',
		margin: {l: 70, r: 10, t: 10, b: 20},

		xaxis: {
			autorange: true,
			domain: [0, 1],
			gridcolor: '#2f2f2f',
			rangeslider: {visible: false},
			showgrid: true,
			showline: false,
			showticklabels: true,
			tickfont: {color: '#ccc', size: 10},
			'tickformat': '%H:%M\n%d %b',
			zeroline: false,
		},

		yaxis: {
			domain: [0.35, 1],
			tickformat: '.4r',
//			tickformat: '%',
            hoverformat: '.8f',
			autorange: true,
			fixedrange: false,
			showticklabels: true,
			gridcolor: '#2f2f2f',
			tickfont: {color: '#cccccc', size: 10},
//            showspikes: true,
//            spikemode: 'across + toaxis',
//            spikedash: 'solid',
//            spikesnap: 'cursor',
//            showline: true,
		},

		yaxis2: {
			domain: [0, 0.13],
			tickformat: '.2r',
			gridcolor: '#3f3f3f',
			showline: false,
			showticklabels: true,
			zeroline: false,
			tickfont: {color: '#ccc', size: 10},
			hoverformat: '.4r',
		},

		yaxis3: {
			domain: [0.16, 0.28],
			tickformat: '.2r',
			showticklabels: false,
			showline: false,
			zeroline: false,
			tickfont: {color: '#ccc', size: 10},
		},

		yaxis4: {
			overlaying: 'y2',
			tickformat: '.2r',
			tickvals: [30, 70],
			gridcolor: '#3f3f3f',
			showticklabels: true,
			showline: false,
			zeroline: false,
			tickfont: {color: '#ccc', size: 10},
		},
//        yaxis5: {
//            overlaying: 'y',
//			domain: [0.35, 1],
//            tickformat: '.1%',
//            range: [0.000021, 0.0000235],
//			autorange: true,
////			fixedrange: false,
////			fixedrange: true,
//			showticklabels: true,
//			gridcolor: '#2f2f2f',
//			tickfont: {color: '#cccccc', size: 10},
//		},
	};
}

var config = {
    responsive: true,
    scrollZoom: true,
    modeBarButtonsToRemove: ['toImage', 'zoom2d', 'lasso2d', 'zoomOut2d', 'zoomIn2d', 'select2d', 'pan2d', 'resetScale2d', 'autoScale2d'],
    displaylogo: false
}