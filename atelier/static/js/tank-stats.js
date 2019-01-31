let TANK_COLOR = "#e9e9e9"
let CITY_COLOR = "#ff6961"
let WELL_COLOR = "#aec5e0"
let WATER_COLOR = "#aec5e0"
let downloadWaterConsumption = document.getElementById("download-water-consumption")
let downloaderPowerConsumption = document.getElementById("download-power-consumption")
let loaderWaterConsumption = document.getElementById("loader-water-consumption")
let loaderTankLevel = document.getElementById("loader-tank-level")
let loaderPowerConsumption = document.getElementById("loader-power-consumption")

function add(a, b) {
    return a + b;
}    

function plotHistoryOverTime(xTank, xCity, xWell, yTank, yCity, yWell) {
    yCity = yCity.map(x => -1 * x)
    yTank = yTank.map(x => -1 * x)
    
    Plotly.newPlot(
        document.getElementById("water_consumption_plot"),
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
            modebar: {
                orientation: "v",
            },
            barmode: "relative",
            margin: {t: 30, r: 20},
            xaxis: {
                showline: false,
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
        document.getElementById("water_consumption_stats_plot"),
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
            margin: {t: 50, r: 10, l: 40},
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

function plotPowerConsumptionStats(pumpIn, pumpOut, city, unit) {
    pumpIn = pumpIn.reduce(add, 0)
    pumpOut = pumpOut.reduce(add, 0)
    city = city.reduce(add, 0)
    let total = (pumpIn + pumpOut + city).toPrecision(2)

    Plotly.newPlot(
        document.getElementById("power_consumption_stats_plot"),
        [{
            type: "pie",
            hoverinfo: "label+value",
            hole: .6,
            values: [pumpIn.toPrecision(2), pumpOut.toPrecision(2), city.toPrecision(2)],
            labels: ["Puits", "Surpresseur", "Ville"],
            marker: { colors: [WELL_COLOR, TANK_COLOR, CITY_COLOR] },
        }],
        {
            showlegend: false,
            margin: {t: 50, r: 10, l: 30},
            title: {
                text: "Total",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
            },
            annotations: [{
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
                showarrow: false,
                text: total + " " + unit,
                x: 0.5,
                y: 0.5,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }]
        }
    )
}

function plotPowerConsumptionHistory(x, pumpIn, pumpOut, city, unit) {
    pumpIn = pumpIn.map(x => x.toPrecision(2))
    pumpOut = pumpOut.map(x => x.toPrecision(2))
    city = city.map(x => x.toPrecision(2))

    Plotly.newPlot(
        document.getElementById("power_consumption_plot"),
        [{
            type: "bar",
            x: x,
            y: pumpIn,
            name: "Puits",
            mode: "lines",
            hoverinfo: "x+y",
            marker: { color: WELL_COLOR },
        }, {
            type: "bar",
            x: x,
            y: pumpOut,
            name: "Surpresseur",
            mode: "lines",
            hoverinfo: "x+y",
            marker: { color: TANK_COLOR },
        }, {
            type: "bar",
            x: x,
            y: city,
            name: "Ville",
            mode: "lines",
            hoverinfo: "x+y",
            marker: { color: CITY_COLOR },
        }],
        {
            barmode: "relative",
            margin: {t: 10, r: 10},
            xaxis: {
                fixedrange: true,
                showline: true,
                zeroline: false,
            },
            yaxis: {
                title: "Consommation (" + unit + ")",
                showline: true,
                zeroline: false,
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

function updateHistoryPlot() {
    downloadWaterConsumption.style.visibility = "hidden"
    loaderWaterConsumption.style.visibility = "visible"

    var period = document.getElementById("period-water-consumption").value
    var timestep = document.getElementById("timestep-water-consumption").value

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
            let csv = "date,puits (L),cuve (L),ville (L)\r\n"
            for (let i = 0; i < data.x_tank.length; i++) {
                csv += (
                    data.x_tank[i] + "," + data.y_well[i] + "," + data.y_tank[i] + "," +
                    data.y_city[i] + "\r\n"
                )
            }
            buildDownloadLink(downloadWaterConsumption, "consommation_eau", period, timestep, csv)
            loaderWaterConsumption.style.visibility = "hidden"
        }
    };
    xhttp.open(
        "GET",
        WATER_CONSUMPTION_URL + "?days=" + encodeURIComponent(period) + "&timestep=" + encodeURIComponent(timestep),
        true
    );
    xhttp.send();
}

function updatePowerConsumptionPlot() {
    downloaderPowerConsumption.style.visibility = "hidden"
    loaderPowerConsumption.style.visibility = "visible"

    var period = document.getElementById("period-power-consumption").value
    var timestep = document.getElementById("timestep-power-consumption").value
    var unit = document.getElementById("unit-power-consumption").value

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttp.responseText)

            // min -> h
            data.pump_in = data.pump_in.map(x => x / 60.0)
            data.pump_out = data.pump_out.map(x => x / 60.0)
            data.city = data.city.map(x => x / 60.0)

            if (unit == "kWh") {
                data.pump_in = data.pump_in.map(x => x * PUMP_IN_POWER / 1000.0)
                data.pump_out = data.pump_out.map(x => x * PUMP_OUT_POWER / 1000.0)
                data.city = data.city.map(x => x * URBAN_NETWORK_POWER / 1000.0)
            }

            plotPowerConsumptionHistory(
                data.dates,
                data.pump_in,
                data.pump_out,
                data.city,
                unit
            )
            plotPowerConsumptionStats(
                data.pump_in,
                data.pump_out,
                data.city,
                unit
            )
            let csv = "date,puits (" + unit + "),cuve (" + unit + "),ville (" + unit + ")\r\n"
            for (let i = 0; i < data.dates.length; i++) {
                csv += (
                    data.dates[i] + "," + data.pump_in[i] + "," + data.pump_out[i] + "," + data.city[i]
                    + "\r\n"
                )
            }
            buildDownloadLink(downloaderPowerConsumption, "consommation_electrique", period, timestep, csv)
            loaderPowerConsumption.style.visibility = "hidden"
        }
    };
    xhttp.open(
        "GET",
        POWER_CONSUMPTION_URL + "?days=" + encodeURIComponent(period) + "&timestep=" + encodeURIComponent(timestep),
        true
    );
    xhttp.send();
}

function buildDownloadLink(link, prefix, period, timestep, csv) {
    let csvContent = "data:text/csv;charset=utf-8," + csv;
    let encodedUri = encodeURI(csvContent)
    let now = new Date()
    let datetime = (
        now.getFullYear() + "_" + (now.getMonth() + 1) + "_" + now.getDate() +
        "_" + now.getHours() + "_" + now.getMinutes()
    )
    link.setAttribute("href", encodedUri)
    link.setAttribute(
        "download",
        prefix + "_" + datetime + "_" + period + "jours_" + timestep + "minutes.csv"
    )
    link.style.visibility = "visible"
}

function plotTankLevelPlot(x, y) {
    y = y.map(x => x + VOLUME_BELOW_LOW_SENSOR)
    Plotly.newPlot(
        document.getElementById("tank_level_plot"),
        [{
            x: x,
            y: y,
            mode: "lines",
            marker: { color: WATER_COLOR },
        }],
        {
            margin: {t: 10, r: 10},
            height: 300,
            xaxis: {
                fixedrange: true,
                showline: true,
                zeroline: false,
            },
            yaxis: {
                title: "Volume (L)",
                showline: true,
                zeroline: false,
                fixedrange: true,
                range: [0, VOLUME_BETWEEN_SENSORS + VOLUME_BELOW_LOW_SENSOR],
            },
        }
    )
}

function updateTankLevelPlot() {
    loaderTankLevel.style.display = "block"
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttp.responseText)
            plotTankLevelPlot(data.dates, data.volumes)
            loaderTankLevel.style.display = "none"
        }
    }
    xhttp.open("GET", TANK_LEVEL_URL, true)
    xhttp.send()
}

document.getElementById("period-water-consumption").addEventListener("change", updateHistoryPlot)
document.getElementById("timestep-water-consumption").addEventListener("change", updateHistoryPlot)
document.getElementById("period-power-consumption").addEventListener("change", updatePowerConsumptionPlot)
document.getElementById("timestep-power-consumption").addEventListener("change", updatePowerConsumptionPlot)
document.getElementById("unit-power-consumption").addEventListener("change", updatePowerConsumptionPlot)

updateHistoryPlot()
updateTankLevelPlot()
updatePowerConsumptionPlot()
