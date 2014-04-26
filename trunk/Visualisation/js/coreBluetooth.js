var margin = {
    top: 0,
    right: 0,
    bottom: 100,
    left: 40
},
    width = 960 - margin.left - margin.right,
    height = 430 - margin.top - margin.bottom,

    gridSize = Math.floor(width / 100),
    legendElementWidth = gridSize * 2,
    buckets = 2,
	colors = ["#ffffff", "#C8C8C8", "#484848", "#000000"];
    colorsDesc = {"#ffffff" : "On", "#C8C8C8": "Probably on", "#484848" : "Probably off", "#000000" : "Off"};
	
var selectedUsers = [];

var parseDate = d3.time.format("%Y%m%d").parse;

var x = d3.time.scale()
    .range([0, width - gridSize]);

var y = d3.scale.ordinal()
    .rangeRoundBands([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function (d) {
        return "<strong>User: </strong>" + d.username;
    })
	
function copyToClipboard() {
	var text = selectedUsers.join();
    window.prompt("Copy to clipboard: Ctrl+C, Enter", text);
}

function clearSelection() {
    document.getElementById("userselect").options.length = 0;
    selectedUsers = [];
	d3.selectAll("rect.bordered.selected").classed("selected", false);
}

// Event handlers for select
function removeOption(selectId) {
    var x = document.getElementById(selectId);
    d3.selectAll("rect.bordered.selected").each(function (d) {
        if (d.username == x.options[x.selectedIndex].text)
            d3.select(this).classed("selected", false);
    })
    x.remove(x.selectedIndex);
	selectedUsers.splice(x.selectedIndex, 1);
};

d3.tsv("data.tsv",
    function (d) {
        return {
            username: d.username,
            date: parseDate(d.date),
            value: +d.value
        };
    },
    function (error, data) {
		//console.log(data)
        var colorScale = d3.scale.quantile()
            .domain([0, buckets - 1, d3.max(data, function (d) {
                return d.value;
            })])
            .range(colors);

        x.domain(d3.extent(data, function (d) {
            return d.date;
        }));

        y.domain(data.map(function (d) {
            return d.username;
        }));

        var svg = d3.select("#chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		svg.call(tip);
		
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(" + gridSize / 2 + "," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(0," + gridSize / 2 + ")")
            .call(yAxis);

        var heatMap = svg.selectAll(".user")
            .data(data)
            .enter().append("rect")
            .attr("x", function (d) {
                return x(d.date);
            })
            .attr("y", function (d) {
                return y(d.username) + y.rangeBand() / 2;
            })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("class", "hour bordered")
            .attr("width", gridSize)
            .attr("height", gridSize)
            .style("fill", function (d) {
                return colorScale(d.value);
            })
			.classed("selected", false)
			.on('mouseover', function (d) {
            tip.show(d);
        })
        .on('mouseout', tip.hide)
		.on('dblclick', function (d) {

            if (selectedUsers.indexOf(d.username) < 0) {
                selectedUsers.push(d.username);

                var x = document.getElementById("userselect");
                var option = document.createElement("option");
                option.text = d.username;
                x.add(option, x[0]);
                d3.select(this).classed("selected", true);

                svg.selectAll("rect").each(function (dd) {
                    if (d.username == dd.username) {
                        d3.select(this).classed("selected", true);
                    }
                })
            } else {
                // remove from list
                var x = document.getElementById("userselect");
                for (var i = 0; i < x.length; i++) {
                    if (x.options[i].value == d.username)
                        x.remove(i);
                }
                // remove from selected users
                selectedUsers.splice(selectedUsers.indexOf(d.username), 1);

                d3.selectAll("rect.bordered.selected").each(function (dd) {
                    if (dd.username == d.username)
                        d3.select(this).classed("selected", false);
                })
            }
        })
		
	d3.select("#check1").on("change", change);
		   
	function change() {

    // Copy-on-write since tweens are evaluated after a delay.
    var y0 = y.domain(data.sort(this.checked
        ? function(a, b) { console.log(b.value - a.value); return b.value - a.value; }
        : function(a, b) { console.log(d3.descending(a.username, b.username)); return d3.ascending(a.username, b.username); })
        .map(function(d) { return d.username; }))
        .copy();
	
    var transition = svg.transition().duration(750),
        delay = function(d, i) { return i * 50; };

    transition.selectAll("rect")
        .delay(delay)
        .attr("y", function(d) { 

		var lala = y0(d.username) + y.rangeBand() / 2;
		console.log(d.username + " " + lala)
		return y0(d.username) + y.rangeBand() / 2; 
		});

    transition.select(".y.axis")
        .call(yAxis)
      .selectAll("g")
        .delay(delay);
  }

        heatMap.append("title").text(function (d) {
            return d.value;
        });
    });
	
var legendContainer = d3.select("#legend").append("svg")
            .attr("width", 200)
            .attr("height", 130)
            .append("g")
            .attr("transform", "translate(" + 0 + "," + margin.top + ")");
			
var legend = legendContainer.selectAll(".legend")
            .data([0].concat(colors), function (d) {
                return d;
            })
            .enter().append("g")
            .attr("class", "legend");

        legend.append("rect")
            .attr("x", function (d, i) {
                return ;
            })
            .attr("y", function (d, i) {
				console.log(gridSize * i * 1.1)
                return gridSize * i * 1.1;
            })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("class", "legend")
            .attr("width", gridSize)
            .attr("height", gridSize)
            .style("fill", function (d, i) {
                return colors[i];
            });

        legend.append("text")
            .attr("class", "mono")
            .text(function (d) {
				console.log(colorsDesc[d])
                return colorsDesc[d];
            })
            .attr("x", function (d, i) {
                return gridSize * 1.5;
            })
            .attr("y", function (d, i) {
				console.log(gridSize * i * 1.1)
                return gridSize * i * 1.1 - gridSize/2;
            });