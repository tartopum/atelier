let TANK_COLOR = "#e9e9e9"
let CITY_COLOR = "#ff6961"
let WELL_COLOR = "#aec5e0"

function plotHistoryOverTime(xTank, xCity, xWell, yTank, yCity, yWell) {
    yCity = yCity.map(x => -1 * x)
    yTank = yTank.map(x => -1 * x)
    
    Plotly.newPlot(
        document.getElementById("history_time_plot"),
        [{
            type: "bar",
            x: xWell,
            y: yWell,
            name: "Collecté du puits",
            hoverinfo: "x+y",
            marker: {
                color: WELL_COLOR,
            },
        }, {
            type: "bar",
            x: xTank,
            y: yTank,
            name: "Consommé sur la cuve",
            hoverinfo: "x+y",
            marker: {
                color: TANK_COLOR,
            },
        }, {
            type: "bar",
            x: xCity,
            y: yCity,
            name: "Consommé sur la ville",
            hoverinfo: "x+y",
            marker: {
                color: CITY_COLOR,
            },
        }],
        {
            barmode: "relative",
            margin: {t: 30, r: 10},
            xaxis: {
                showline: false,
                fixedrange: true,
            },
            yaxis: {
                title: "Volume (L)",
                showline: true,
                zeroline: false,
                range: [0, null],
                fixedrange: true,
            },
            legend: {
                x: 0.5,
                y: 1.1,
                orientation: "h",
                xanchor: "center",
            },
            shapes: [{
                type: "line",
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 0,
                xref: "paper",
                line: {width: 1},
            }],
        }
    )
}

function plotHistoryStats(yTank, yCity, yWell) {
    function add(a, b) {
        return a + b;
    }    

    let sumTank = yTank.reduce(add, 0)
    let sumCity = yCity.reduce(add, 0)
    let sumWell = yWell.reduce(add, 0)

    let meanTank = Math.round(sumTank / yTank.length)
    let meanCity = Math.round(sumCity / yCity.length)
    let meanWell = Math.round(sumWell / yWell.length)

    let minTank = Math.min(...yTank)
    let minCity = Math.min(...yCity)
    let minWell = Math.min(...yWell)

    let maxTank = Math.max(...yTank)
    let maxCity = Math.max(...yCity)
    let maxWell = Math.max(...yWell)

    Plotly.newPlot(
        document.getElementById("history_stats_plot"),
        [{
            type: "bar",
            x: ["Puits", "Cuve", "Ville"],
            y: [sumWell, sumTank, sumCity],
            hoverinfo: "skip",
            text: [sumWell, sumTank, sumCity],
            textposition: "auto",
            marker: {
                color: [WELL_COLOR, TANK_COLOR, CITY_COLOR],
            },
        }, {
            type: "bar",
            x: ["Puits", "Cuve", "Ville"],
            y: [meanWell, meanTank, meanCity],
            hoverinfo: "skip",
            text: [meanWell, meanTank, meanCity],
            textposition: "auto",
            xaxis: "x2",
            yaxis: "y2",
            marker: {
                color: [WELL_COLOR, TANK_COLOR, CITY_COLOR],
            },
        }, {
            type: "bar",
            x: ["Puits", "Cuve", "Ville"],
            y: [minWell, minTank, minCity],
            hoverinfo: "skip",
            text: [minWell, minTank, minCity],
            textposition: "auto",
            xaxis: "x3",
            yaxis: "y3",
            marker: {
                color: [WELL_COLOR, TANK_COLOR, CITY_COLOR],
            },
        }, {
            type: "bar",
            x: ["Puits", "Cuve", "Ville"],
            y: [maxWell, maxTank, maxCity],
            hoverinfo: "skip",
            text: [maxWell, maxTank, maxCity],
            textposition: "auto",
            xaxis: "x4",
            yaxis: "y4",
            marker: {
                color: [WELL_COLOR, TANK_COLOR, CITY_COLOR],
            },
        }],
        {
            grid: {rows: 2, columns: 2, pattern: "independent"},
            barmode: "grouped",
            showlegend: false,
            margin: {t: 30, r: 10, l: 30},
            xaxis: {
                showline: true,
                fixedrange: true,
            },
            xaxis2: {
                showline: true,
                fixedrange: true,
                tickvals: [],
            },
            xaxis3: {
                showline: true,
                fixedrange: true,
                tickvals: [],
            },
            xaxis4: {
                showline: true,
                fixedrange: true,
                tickvals: [],
            },
            yaxis: {
                showline: true,
                zeroline: false,
                fixedrange: true,
            },
            yaxis2: {
                showline: true,
                zeroline: false,
                fixedrange: true,
            },
            yaxis3: {
                showline: true,
                zeroline: false,
                fixedrange: true,
            },
            yaxis4: {
                showline: true,
                zeroline: false,
                fixedrange: true,
            },
            annotations: [{
                x: 0.25,
                y: 1,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "bottom",
                text: "Total",
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 20,
                },
            }, {
                x: 0.75,
                y: 1,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "bottom",
                text: "Moyenne",
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 20,
                },
            }, {
                x: 0.25,
                y: 0.5,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "top",
                text: "Minimum",
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 20,
                },
            }, {
                x: 0.75,
                y: 0.5,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "top",
                text: "Maximum",
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 20,
                },
            }]
        }
    )
}

function updateHistoryPlot() {
    var period = document.getElementById("period").value
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttp.responseText)
            plotHistoryOverTime(
                data.x_tank,
                data.x_city,
                data.x_well,
                data.y_tank,
                data.y_city,
                data.y_well
            )
            plotHistoryStats(
                data.y_tank,
                data.y_city,
                data.y_well
            )
        }
    };
    xhttp.open("GET", CONSUMPTION_URL + "?days=" + encodeURIComponent(period), true);
    xhttp.send();
}

document.getElementById("period").addEventListener("change", updateHistoryPlot)

updateHistoryPlot()
