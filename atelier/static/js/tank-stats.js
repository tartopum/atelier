function plotConsumption(xTank, xCity, yTank, yCity) {
    Plotly.newPlot(
        document.getElementById("week_consumption_plot"),
        [{
            type: "bar",
            x: xTank,
            y: yTank,
            name: "Cuve",
            hoverinfo: "x+y",
            marker: {
                color: "#e9e9e9",
            },
        }, {
            type: "bar",
            x: xCity,
            y: yCity,
            name: "Ville",
            hoverinfo: "x+y",
            marker: {
                color: "#ff6961",
            },
        }],
        {
            barmode: "stack",
            margin: {t: 10},
            yaxis: {
                title: "Volume (L)",
                showline: true,
                range: [0, null],
            },
            legend: {
                x: 0,
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
