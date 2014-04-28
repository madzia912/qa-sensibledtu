// Settings common for all diagrams ////////////////////////////////

var margin = {
        top: 20,
        right: 80,
        bottom: 50,
        left: 50
    },
    width = 960 - margin.left - margin.right,
    height = 450 - margin.top - margin.bottom;

var selectedUsersBluetooth = [];
var selectedUsersWifi = [];
var selectedUsersLocation = [];

var markSize = 2;
var widthExtended = width + margin.left + margin.right - 200
var heightExtended = height + margin.top + margin.bottom

var formatPercent = d3.format(".0%");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(formatPercent);

var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function (d) {
        return "<strong>Quality: </strong>" + (d.value * 100).toPrecision(3) + "%";
    })

var currentSorting = {
    'bluetooth': {
        name: 'none',
        colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
    },
    'wifi': {
        name: 'none',
        colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
    },
    'location': {
        name: 'none',
        colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
    }
};

// Buttons functionality
function copyToClipboard(buttonId) {
    var text = "";
    switch (buttonId) {
    case "userselectBluetooth":
        text = selectedUsersBluetooth.join();
        break;
    case "userselectWifi":
        text = selectedUsersWifi.join();
        break;
    case "userselectLocation":
        text = selectedUsersLocation.join();
        break;
    }
    window.prompt("Copy to clipboard: Ctrl+C, Enter", text);
}

function clearSelection(selectId) {
    document.getElementById(selectId).options.length = 0;
    if (selectId == "userselectBluetooth") {
        selectedUsersBluetooth = [];
        chart1.selectAll(".mark.selected").classed("selected", false);
    } else if (selectId == "userselectWifi") {
        selectedUsersWifi = [];
        chart2.selectAll(".mark.selected").classed("selected", false);
    } else if (selectId == "userselectLocation") {
        selectedUsersLocation = [];
        chart3.selectAll(".mark.selected").classed("selected", false);
    }
}

// Event handlers for select
function removeOption(selectId) {
    var x = document.getElementById(selectId);
    d3.selectAll(".mark.selected").each(function (d) {
        if (d.username == x.options[x.selectedIndex].text)
            d3.select(this).classed("selected", false);
    })
    x.remove(x.selectedIndex);

    switch (selectId) {
    case "userselectBluetooth":
        selectedUsersBluetooth.splice(x.selectedIndex, 1);
        break;
    case "userselectWifi":
        selectedUsersWifi.splice(x.selectedIndex, 1);
        break;
    case "userselectLocation":
        selectedUsersLocation.splice(x.selectedIndex, 1);
        break;
    }

};

// Mouse handlers

function mouseDownHandler(chart, p) {
    chart.selectAll("rect.selection").remove();
    chart.append("rect")
        .attr({
            rx: 6,
            ry: 6,
            class: "selection",
            x: p[0] - margin.left,
            y: p[1] - margin.top,
            width: 0,
            height: 0
        });
}

function mouseMoveHandler(chart, p) {
    var s = chart.select("rect.selection");
    if (!s.empty()) {
        var d = {
                x: parseInt(s.attr("x"), 10),
                y: parseInt(s.attr("y"), 10),
                width: parseInt(s.attr("width"), 10),
                height: parseInt(s.attr("height"), 10)
            },
            move = {
                x: p[0] - margin.left - d.x,
                y: p[1] - margin.top - d.y
            };
        if (move.x < 1 || (move.x * 2 < d.width)) {
            d.x = p[0] - margin.left;
            d.width -= move.x;
        } else {
            d.width = move.x;
        }

        if (move.y < 1 || (move.y * 2 < d.height)) {
            d.y = p[1] - margin.top;
            d.height -= move.y;
        } else {
            d.height = move.y;
        }
        s.attr(d);
    }
}

function mouseUpHandler(chart, selectedUsers, userSelectId, currentSort) {
    s = chart.select("rect");
    var rectVal = {
        left: parseInt(s.attr("x")),
        right: parseInt(s.attr("x")) + parseInt(s.attr("width")),
        top: parseInt(s.attr("y")),
        bottom: parseInt(s.attr("y")) + parseInt(s.attr("height"))
    };

    if (rectVal.left > 0) // the selection is in the diagram
    {
        // get all points inside selection
        chart.selectAll("circle.mark").each(function (d) {
            // get all nodes inside rectangle
            if (parseInt(this.cx.baseVal.value) < rectVal.right && parseInt(this.cx.baseVal.value) > rectVal.left &&
                parseInt(this.cy.baseVal.value) > rectVal.top && parseInt(this.cy.baseVal.value) < rectVal.bottom) {
                d3.select(this).classed("selected", true);
                chart.selectAll(".mark").each(function (dd) {
                    if (d.username == dd.username) {
                        d3.select(this).classed("selected", true);
                        if (selectedUsers.indexOf(d.username) < 0) {
                            var x = document.getElementById(userSelectId);
                            var option = document.createElement("option");
                            option.text = d.username;
                            x.add(option, x[0]);
                            selectedUsers.push(d.username);
                        }
                    }
                })
            }
        });
    } else // the selection was on Yaxis
    {
        chart.selectAll("circle.mark").each(function (d) {
            if (parseInt(this.cy.baseVal.value) > rectVal.top && parseInt(this.cy.baseVal.value) < rectVal.bottom) {
                // check which sorting is right now
                // select all nodes with values on Yaxis
                if (d3.rgb(currentSort.colour).toString() == d3.rgb(getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")).toString() ||
                    d3.rgb(currentSort.colour).toString() == d3.rgb(this.style.fill).toString()) {
                    d3.select(this).classed("selected", true);
                    chart.selectAll(".mark").each(function (dd) {
                        if (d.username == dd.username) {
                            d3.select(this).classed("selected", true);
                            if (selectedUsers.indexOf(d.username) < 0) {
                                var x = document.getElementById(userSelectId);
                                var option = document.createElement("option");
                                option.text = d.username;
                                x.add(option, x[0]);
                                selectedUsers.push(d.username);
                            }
                        }
                    })
                }
            }
        })
    }
    d3.select("rect").remove();
}

// Chart core
function createChart(divId, selectedUsers, selectId, sorting) {
    var chart = d3.select(divId).append("svg")
        .attr("width", width + margin.left + margin.right + 'px')
        .attr("height", height + margin.top + margin.bottom + 'px')
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.select(divId).on("mousedown", function () {
        mouseDownHandler(chart, d3.mouse(this));
    })
        .on("mousemove", function () {
            mouseMoveHandler(chart, d3.mouse(this));
        })
        .on("mouseup", function () {
            mouseUpHandler(chart, selectedUsers, selectId, sorting);
        });

    chart.call(tip);
    return chart;
}

// Chart creation //////////////////////////////////

var chart1 = createChart("#chartbluetooth", selectedUsersBluetooth, "userselectBluetooth", currentSorting.bluetooth);

var chart2 = createChart("#chartwifi", selectedUsersWifi, "userselectWifi", currentSorting.wifi);

var chart3 = createChart("#chartlocation", selectedUsersLocation, "userselectLocation", currentSorting.location);

d3.tsv("databluetooth.tsv", function (error, data) {
    color.domain(d3.keys(data[0]).filter(function (key) {
        return key !== "username";
    }));

    data.forEach(function (d) {
        d.username = d.username;
    });

    var qualities = color.domain().map(function (name) {
        return {
            name: name,
            values: data.map(function (d) {
                return {
                    username: d.username,
                    value: +d[name],
                    color: name,
                    selected: false
                };
            })
        };
    });

    x.domain(data.map(function (d) {
        return d.username;
    }));
    y.domain([
        d3.min(qualities, function (c) {
            return d3.min(c.values, function (v) {
                return v.value;
            });
        }),
        d3.max(qualities, function (c) {
            return d3.max(c.values, function (v) {
                return v.value;
            });
        })
    ]);

    chart1.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    chart1.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Quality")

    var quality = chart1.selectAll(".quality")
        .data(qualities)
        .enter();

    var groups = quality.append("g")
        .attr("class", "quality");

    groups.selectAll("circle")
        .data(
            function (d) {
                return d.values;
            })
        .enter()
        .append("circle")
        .attr("class", "mark")
        .attr("cx", function (d) {
            return x(d.username) + x.rangeBand() / 2;
        })
        .attr("cy", function (d) {
            return y(d.value);
        })
        .attr("r", markSize)
        .style("fill", function (d) {
            return color(d.color);
        })
        .classed("selected", false)
        .on('mouseover', function (d) {
            tip.show(d);
        })
        .on('mouseout', tip.hide)
        .on('dblclick', function (d) {
            if (selectedUsersBluetooth.indexOf(d.username) < 0) {
                selectedUsersBluetooth.push(d.username);

                var x = document.getElementById("userselectBluetooth");
                var option = document.createElement("option");
                option.text = d.username;
                x.add(option, x[0]);
                d3.select(this).classed("selected", true);

                chart1.selectAll(".mark").each(function (dd) {
                    if (d.username == dd.username) {
                        d3.select(this).classed("selected", true);
                    }
                })
            } else {
                // remove from list
                var x = document.getElementById("userselectBluetooth");
                for (var i = 0; i < x.length; i++) {
                    if (x.options[i].value == d.username)
                        x.remove(i);
                }
                // remove from selected users
                selectedUsersBluetooth.splice(selectedUsersBluetooth.indexOf(d.username), 1);

                d3.selectAll(".mark.selected").each(function (dd) {
                    if (dd.username == d.username)
                        d3.select(this).classed("selected", false);
                })
            }
        })

    ////////////////////////////////////////// SORTING

    d3.select("#none1").on("click", function (d, i) {
        currentSorting.bluetooth = {
            name: 'none',
            colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
        };
        change("none");
    });

    d3.select("#all1").on("click", function (d, i) {
        currentSorting.bluetooth = {
            name: 'all',
            colour: getComputedStyle(document.getElementById('labelall')).getPropertyValue("color")
        };
        change("all");
    });

    d3.select("#month1").on("click", function (d, i) {
        currentSorting.bluetooth = {
            name: 'month',
            colour: getComputedStyle(document.getElementById('labelmonth')).getPropertyValue("color")
        };
        change("month");
    });

    d3.select("#week1").on("click", function (d, i) {
        currentSorting.bluetooth = {
            name: 'week',
            colour: getComputedStyle(document.getElementById('labelweek')).getPropertyValue("color")
        };
        change("week");
    });

    function change(action) {

        var x0 = x.domain(data.sort(function (a, b) {
                    switch (action) {
                    case "none":
                        return d3.ascending(a.username, b.username);
                        break;
                    case "all":
                        return b.all - a.all;
                        break;
                    case "month":
                        return b.month - a.month;
                        break;
                    case "week":
                        return b.week - a.week;
                        break;
                    }
                })
                .map(function (d) {
                    return d.username;
                }))
            .copy();

        var transition = groups.transition().duration(750),
            delay = function (d, i) {
                return i * 5;
            };

        transition.selectAll("circle.mark")
            .delay(delay)
            .attr("cx", function (d) {
                return x0(d.username) + x.rangeBand() / 2;
            });
    }
});

// WIFI //////////////////////////////////////

d3.tsv("datawifi.tsv", function (error, data) {
    color.domain(d3.keys(data[0]).filter(function (key) {
        return key !== "username";
    }));

    data.forEach(function (d) {
        d.username = d.username;
    });

    var qualities = color.domain().map(function (name) {
        return {
            name: name,
            values: data.map(function (d) {
                return {
                    username: d.username,
                    value: +d[name],
                    color: name
                };
            })
        };
    });

    x.domain(data.map(function (d) {
        return d.username;
    }));
    y.domain([
        d3.min(qualities, function (c) {
            return d3.min(c.values, function (v) {
                return v.value;
            });
        }),
        d3.max(qualities, function (c) {
            return d3.max(c.values, function (v) {
                return v.value;
            });
        })
    ]);

    chart2.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function (d) {
            return "rotate(-90)"
        });

    chart2.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Quality");

    var quality = chart2.selectAll(".quality")
        .data(qualities)
        .enter();

    var groups = quality.append("g")
        .attr("class", "quality");

    groups.selectAll("circle")
        .data(
            function (d) {
                return d.values;
            })

    .enter()
        .append("circle")
        .attr("class", "mark")
        .attr("cx", function (d) {
            return x(d.username) + x.rangeBand() / 2;
        })
        .attr("cy", function (d) {
            return y(d.value);
        })
        .attr("r", markSize)
        .style("fill", function (d) {
            return color(d.color);
        })
        .on('mouseover', function (d) {
            tip.show(d);
        })
        .on('mouseout', tip.hide)
        .on('dblclick', function (d) {

            if (selectedUsersWifi.indexOf(d.username) < 0) {
                selectedUsersWifi.push(d.username);

                var x = document.getElementById("userselectWifi");
                var option = document.createElement("option");
                option.text = d.username;
                x.add(option, x[0]);
                d3.select(this).classed("selected", true);

                chart2.selectAll(".mark").each(function (dd) {
                    if (d.username == dd.username) {
                        d3.select(this).classed("selected", true);
                    }
                })
            } else {
                // remove from list
                var x = document.getElementById("userselectWifi");
                for (var i = 0; i < x.length; i++) {
                    if (x.options[i].value == d.username)
                        x.remove(i);
                }
                // remove from selected users
                selectedUsersWifi.splice(selectedUsersWifi.indexOf(d.username), 1);

                d3.selectAll(".mark.selected").each(function (dd) {
                    if (dd.username == d.username)
                        d3.select(this).classed("selected", false);
                })
            }
        })


    ////////////////////////////////////////// SORTING

    d3.select("#none2").on("click", function (d, i) {
        currentSorting.wifi = {
            name: 'none',
            colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
        };
        change("none");
    });

    d3.select("#all2").on("click", function (d, i) {
        currentSorting.wifi = {
            name: 'all',
            colour: getComputedStyle(document.getElementById('labelall')).getPropertyValue("color")
        };
        change("all");
    });

    d3.select("#month2").on("click", function (d, i) {
        currentSorting.wifi = {
            name: 'month',
            colour: getComputedStyle(document.getElementById('labelmonth')).getPropertyValue("color")
        };
        change("month");
    });

    d3.select("#week2").on("click", function (d, i) {
        currentSorting.wifi = {
            name: 'week',
            colour: getComputedStyle(document.getElementById('labelweek')).getPropertyValue("color")
        };
        change("week");
    });

    function change(action) {

        var x0 = x.domain(data.sort(function (a, b) {
                    switch (action) {
                    case "none":
                        return d3.ascending(a.username, b.username);
                        break;
                    case "all":
                        return b.all - a.all;
                        break;
                    case "month":
                        return b.month - a.month;
                        break;
                    case "week":
                        return b.week - a.week;
                        break;
                    }
                })
                .map(function (d) {
                    return d.username;
                }))
            .copy();

        var transition = groups.transition().duration(750),
            delay = function (d, i) {
                return i * 5;
            };

        transition.selectAll("circle.mark")
            .delay(delay)
            .attr("cx", function (d) {
                return x0(d.username) + x.rangeBand() / 2;
            });
    }
});

// LOCATION ////////////////////////////////////

d3.tsv("datalocation.tsv", function (error, data) {
    color.domain(d3.keys(data[0]).filter(function (key) {
        return key !== "username";
    }));

    data.forEach(function (d) {
        d.username = d.username;
    });

    var qualities = color.domain().map(function (name) {
        return {
            name: name,
            values: data.map(function (d) {
                return {
                    username: d.username,
                    value: +d[name],
                    color: name
                };
            })
        };
    });

    x.domain(data.map(function (d) {
        return d.username;
    }));
    y.domain([
        d3.min(qualities, function (c) {
            return d3.min(c.values, function (v) {
                return v.value;
            });
        }),
        d3.max(qualities, function (c) {
            return d3.max(c.values, function (v) {
                return v.value;
            });
        })
    ]);

    chart3.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function (d) {
            return "rotate(-90)"
        });

    chart3.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Quality");


    var quality = chart3.selectAll(".quality")
        .data(qualities)
        .enter();

    var groups = quality.append("g")
        .attr("class", "quality");

    groups.selectAll("circle")
        .data(
            function (d) {
                return d.values;
            })

    .enter()
        .append("circle")
        .attr("class", "mark")
        .attr("cx", function (d) {
            return x(d.username) + x.rangeBand() / 2;
        })
        .attr("cy", function (d) {
            return y(d.value);
        })
        .attr("r", markSize)
        .style("fill", function (d) {
            return color(d.color);
        })
        .on('mouseover', function (d) {
            tip.show(d);
        })
        .on('mouseout', tip.hide)
        .on('dblclick', function (d) {

            if (selectedUsersLocation.indexOf(d.username) < 0) {
                selectedUsersLocation.push(d.username);

                var x = document.getElementById("userselectLocation");
                var option = document.createElement("option");
                option.text = d.username;
                x.add(option, x[0]);
                d3.select(this).classed("selected", true);

                chart3.selectAll(".mark").each(function (dd) {
                    if (d.username == dd.username) {
                        d3.select(this).classed("selected", true);
                    }
                })
            } else {
                // remove from list
                var x = document.getElementById("userselectLocation");
                for (var i = 0; i < x.length; i++) {
                    if (x.options[i].value == d.username)
                        x.remove(i);
                }
                // remove from selected users
                selectedUsersLocation.splice(selectedUsersLocation.indexOf(d.username), 1);

                d3.selectAll(".mark.selected").each(function (dd) {
                    if (dd.username == d.username)
                        d3.select(this).classed("selected", false);
                })
            }
        })


    ////////////////////////////////////////// SORTING

    d3.select("#none3").on("click", function (d, i) {
        currentSorting.location = {
            name: 'none',
            colour: getComputedStyle(document.getElementById('labelnone')).getPropertyValue("color")
        };
        change("none");
    });

    d3.select("#all3").on("click", function (d, i) {
        currentSorting.location = {
            name: 'all',
            colour: getComputedStyle(document.getElementById('labelall')).getPropertyValue("color")
        };
        change("all");
    });

    d3.select("#month3").on("click", function (d, i) {
        currentSorting.location = {
            name: 'month',
            colour: getComputedStyle(document.getElementById('labelmonth')).getPropertyValue("color")
        };
        change("month");
    });

    d3.select("#week3").on("click", function (d, i) {
        currentSorting.location = {
            name: 'week',
            colour: getComputedStyle(document.getElementById('labelweek')).getPropertyValue("color")
        };
        change("week");
    });

    function change(action) {

        var x0 = x.domain(data.sort(function (a, b) {
                    switch (action) {
                    case "none":
                        return d3.ascending(a.username, b.username);
                        break;
                    case "all":
                        return b.all - a.all;
                        break;
                    case "month":
                        return b.month - a.month;
                        break;
                    case "week":
                        return b.week - a.week;
                        break;
                    }
                })
                .map(function (d) {
                    return d.username;
                }))
            .copy();

        var transition = groups.transition().duration(750),
            delay = function (d, i) {
                return i * 5;
            };

        transition.selectAll("circle.mark")
            .delay(delay)
            .attr("cx", function (d) {
                return x0(d.username) + x.rangeBand() / 2;
            });
    }
});