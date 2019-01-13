function plotConsumption(xTank, xCity, yTank, yCity) {
    let TANK_COLOR = "#e9e9e9"
    let CITY_COLOR = "#ff6961"

    function add(a, b) {
        return a + b;
    }    

    let sumTank = yTank.reduce(add, 0)
    let sumCity = yCity.reduce(add, 0)

    let annotations = []
    if (sumTank) {
        annotations.push({
            x: 0,
            y: sumTank / 2.0,
            text: sumTank + "L",
            showarrow: false,
            bgcolor: TANK_COLOR,
            font: {
                color: "black",
            },
        })
    }
    if (sumCity) {
        annotations.push({
            x: 0,
            y: sumTank + sumCity / 2.0,
            text: sumCity + "L",
            showarrow: false,
            bgcolor: CITY_COLOR,
            font: {
                color: "black",
            },
        })
    }

    Plotly.newPlot(
        document.getElementById("week_consumption_summary_plot"),
        [{
            type: "bar",
            x: [0],
            y: [sumTank],
            name: "Cuve",
            hoverinfo: "skip",
            marker: {
                color: TANK_COLOR,
            },
        }, {
            type: "bar",
            x: [0],
            y: [sumCity],
            name: "Ville",
            hoverinfo: "skip",
            marker: {
                color: CITY_COLOR,
            },
        }],
        {
            title: "Total",
            width: 100,
            barmode: "stack",
            showlegend: false,
            margin: {t: 30, r: 10, l: 10},
            xaxis: {
                visible: false,
                fixedrange: true,
            },
            yaxis: {
                visible: false,
                fixedrange: true,
            },
            legend: {
                x: 0.5,
                y: 1.1,
                orientation: "h",
            },
            annotations: annotations,
        }
    )
    Plotly.newPlot(
        document.getElementById("week_consumption_plot"),
        [{
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
            barmode: "stack",
            margin: {t: 30, r: 10},
            xaxis: {
                showline: true,
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
            },
        }
    )
}

function updateConsumptionPlot() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttp.responseText)
            plotConsumption(data.x_tank, data.x_city, data.y_tank, data.y_city)
        }
    };
    xhttp.open("GET", HOURLY_CONSUMPTION_URL, true);
    xhttp.send();
}

updateConsumptionPlot();
