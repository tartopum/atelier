function plotConsumption(xTank, xCity, xWell, yTank, yCity, yWell) {
    let TANK_COLOR = "#e9e9e9"
    let CITY_COLOR = "#ff6961"
    let WELL_COLOR = "#aec5e0"

    function add(a, b) {
        return a + b;
    }    

    let sumTank = yTank.reduce(add, 0)
    let sumCity = yCity.reduce(add, 0)
    let sumWell = yWell.reduce(add, 0)
    let totalScale = Math.max(sumWell, sumTank + sumCity)

    yCity = yCity.map(x => -1 * x)
    yTank = yTank.map(x => -1 * x)

    Plotly.newPlot(
        document.getElementById("week_consumption_summary_plot"),
        [{
            type: "bar",
            x: [0],
            y: [-sumTank],
            name: "Cuve",
            hoverinfo: "y",
            marker: {
                color: TANK_COLOR,
            },
        }, {
            type: "bar",
            x: [0],
            y: [-sumCity],
            name: "Ville",
            hoverinfo: "y",
            marker: {
                color: CITY_COLOR,
            },
        }, {
            type: "bar",
            x: [0],
            y: [sumWell],
            name: "Puits",
            hoverinfo: "y",
            marker: {
                color: WELL_COLOR,
            },
        }],
        {
            title: {
                text: "Total",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                },
            },
            width: 100,
            barmode: "relative",
            showlegend: false,
            margin: {t: 30, r: 10, l: 30},
            xaxis: {
                visible: false,
                fixedrange: true,
            },
            yaxis: {
                showgrid: false,
                zeroline: false,
                fixedrange: true,
                tickvals: [0, sumWell, -sumTank, -sumTank-sumCity],
            },
        }
    )
    Plotly.newPlot(
        document.getElementById("week_consumption_plot"),
        [{
            type: "bar",
            x: xWell,
            y: yWell,
            name: "Puits",
            hoverinfo: "x+y",
            marker: {
                color: WELL_COLOR,
            },
        }, {
            type: "bar",
            x: xTank,
            y: yTank,
            name: "Cuve",
            hoverinfo: "x+y",
            marker: {
                color: TANK_COLOR,
            },
        }, {
            type: "bar",
            x: xCity,
            y: yCity,
            name: "Ville",
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
                zeroline: true,
                range: [0, null],
                fixedrange: true,
            },
            legend: {
                x: 0.5,
                y: 1.1,
                orientation: "h",
                xanchor: "center",
            },
        }
    )
}

function updateConsumptionPlot() {
    var period = document.getElementById("period").value
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttp.responseText)
            plotConsumption(
                data.x_tank,
                data.x_city,
                data.x_well,
                data.y_tank,
                data.y_city,
                data.y_well
            )
        }
    };
    xhttp.open("GET", CONSUMPTION_URL + "?days=" + encodeURIComponent(period), true);
    xhttp.send();
}

document.getElementById("period").addEventListener("change", updateConsumptionPlot)

updateConsumptionPlot()
