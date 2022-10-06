// data point will need to adjust accordingly

var root = am5.Root.new("chartdiv");
root.setThemes([am5themes_Dark.new(root)]);

var chart = root.container.children.push(
	am5xy.XYChart.new(root, {
		panX: true,
		panY: true,
		wheelX: "panX",
		wheelY: "zoomX",
		pinchZoomX: true,
	})
);

var cursor = chart.set(
	"cursor",
	am5xy.XYCursor.new(root, {
		behavior: "none",
	})
);
cursor.lineY.set("visible", false);

// Generate random data
var backDate = new Date(2022, 0, 1);
backDate.setHours(0, 0, 0, 0);
var value = 1000;
var previousValue = value;
var downColor = root.interfaceColors.get("negative");
var upColor = root.interfaceColors.get("positive");
var color;
var previousColor;
var previousDataObj;

function generateData() {
	value = Math.round(Math.random() * 15 - 8 + value);
	am5.time.add(backDate, "day", 1);

	if (value >= previousValue) {
		color = upColor;
	} else {
		color = downColor;
	}
	previousValue = value;

	var dataObj = { date: backDate.getTime(), value: value, color: color };

	if (color != previousColor) {
		if (!previousDataObj) {
			previousDataObj = dataObj;
		}
		previousDataObj.strokeSettings = { stroke: color };
	}

	previousDataObj = dataObj;
	previousColor = color;

	return dataObj;
}

function generateDatas(count) {
	var data = [];
	for (var i = 0; i < count; ++i) {
		data.push(generateData());
	}
	return data;
}

var xAxis = chart.xAxes.push(
	am5xy.DateAxis.new(root, {
		baseInterval: { timeUnit: "day", count: 1 },
		renderer: am5xy.AxisRendererX.new(root, {}),
		tooltip: am5.Tooltip.new(root, {}),
	})
);

var yAxis = chart.yAxes.push(
	am5xy.ValueAxis.new(root, {
		renderer: am5xy.AxisRendererY.new(root, {}),
	})
);

var series = chart.series.push(
	am5xy.LineSeries.new(root, {
		name: "Series",
		xAxis: xAxis,
		yAxis: yAxis,
		valueYField: "value",
		valueXField: "date",
	})
);

series.strokes.template.set("templateField", "strokeSettings");

var tooltip = series.set(
	"tooltip",
	am5.Tooltip.new(root, {
		labelText: "{valueY}",
	})
);

tooltip.on("pointTo", function () {
	var background = tooltip.get("background");
	background.set("fill", background.get("fill"));
});

tooltip.get("background").adapters.add("fill", function (fill) {
	if (tooltip.dataItem) {
		return tooltip.dataItem.dataContext.color;
	}
	return fill;
});

var scrollbar = chart.set(
	"scrollbarX",
	am5xy.XYChartScrollbar.new(root, {
		orientation: "horizontal",
		height: 60,
	})
);

var sbDateAxis = scrollbar.chart.xAxes.push(
	am5xy.DateAxis.new(root, {
		baseInterval: {
			timeUnit: "day",
			count: 1,
		},
		renderer: am5xy.AxisRendererX.new(root, {}),
	})
);

var sbValueAxis = scrollbar.chart.yAxes.push(
	am5xy.ValueAxis.new(root, {
		renderer: am5xy.AxisRendererY.new(root, {}),
	})
);

var sbSeries = scrollbar.chart.series.push(
	am5xy.LineSeries.new(root, {
		valueYField: "value",
		valueXField: "date",
		xAxis: sbDateAxis,
		yAxis: sbValueAxis,
	})
);

// Generate and set data
var nowDate = new Date();
var diffTime = nowDate.getTime() - backDate.getTime();
var diffDays = diffTime / (1000 * 3600 * 24);
// console.log(diffDays)
var data = generateDatas(diffDays - 1); // up to  the current date
series.data.setAll(data);
sbSeries.data.setAll(data);

series.appear(1000); // data value point
chart.appear(1000, 100);
