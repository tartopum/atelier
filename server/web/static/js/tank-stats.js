let TANK_COLOR = "#e9e9e9"
let CITY_COLOR = "#ff6961"
let WELL_COLOR = "#aec5e0"
let WATER_COLOR = "#aec5e0"
let downloadWaterConsumption = document.getElementById("download-water-consumption")
let downloaderPowerConsumption = document.getElementById("download-power-consumption")
let loaderWaterConsumption = document.getElementById("loader-water-consumption")
let loaderTankLevel = document.getElementById("loader-tank-level")
let loaderPowerConsumption = document.getElementById("loader-power-consumption")
let loaderWellPumpEfficiency = document.getElementById("loader-well-pump-efficiency")

function add(a, b) {
    return a + b;
}

function displayError(parentId) {
  var children = document.querySelectorAll("#" + parentId + " > *");
  for (var child of children) {
    if (child.className.indexOf("data-error") != -1) {
      child.innerHTML = "Une erreur est survenue au chargement des données.";
      child.style.display = "block";
    } else {
      child.style.display = "none";
    }
  }
}

function hideError(parentId) {
  var children = document.querySelectorAll("#" + parentId + " > *");
  for (var child of children) {
    if (child.className.indexOf("data-error") != -1) {
      child.style.display = "none";
    } else {
      child.style.display = "block";
    }
  }
}

function plotWaterConsumptionHistory(xTank, xCity, xWell, yTank, yCity, yWell, xMin, xMax) {
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
            margin: {t: 30, r: 60},
            xaxis: {
                title: "Heure de début",
                showline: false,
                range: [xMin, xMax],
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

function plotWaterConsumptionStats(yTank, yCity, yWell, timestep, period) {
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
            margin: {t: 80, r: 10, l: 40},
            title: {
                text: "Pendant " + period,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 24,
                },
            },
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
                    size: 18,
                },
            }, {
                x: 0.75,
                y: 1,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "bottom",
                text: "Moy. par " + timestep,
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 18,
                },
            }, {
                x: 0.25,
                y: 0.5,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "top",
                text: "Min. par " + timestep,
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 18,
                },
            }, {
                x: 0.75,
                y: 0.5,
                xref: "paper",
                yref: "paper",
                xanchor: "center",
                yanchor: "top",
                text: "Max. par " + timestep,
                showarrow: false,
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 18,
                },
            }]
        }
    )
}

function plotPowerConsumptionStats(pumpIn, pumpOut, city, unit, period) {
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
                text: "Total sur " + period,
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

function plotPowerConsumptionHistory(x, pumpIn, pumpOut, city, unit, xMin, xMax) {
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
            margin: {t: 10, r: 60},
            xaxis: {
                showline: true,
                zeroline: false,
                title: "Heure de début",
                range: [xMin, xMax],
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

function updateWaterConsumptionPlot() {
    downloadWaterConsumption.style.visibility = "hidden"
    loaderWaterConsumption.style.visibility = "visible"
    hideError("water_consumption_wrapper");

    var periodSelect = document.getElementById("period-water-consumption")
    var timestepSelect = document.getElementById("timestep-water-consumption")
    var period = periodSelect.value
    var timestep = timestepSelect.value

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            loaderWaterConsumption.style.visibility = "hidden"
            if (this.status != 200) {
                displayError("water_consumption_wrapper");
            } else {
                let data = JSON.parse(xhttp.responseText)
                plotWaterConsumptionHistory(
                    data.x_tank,
                    data.x_city,
                    data.x_well,
                    data.y_tank,
                    data.y_city,
                    data.y_well,
                    data.x_min,
                    data.x_max,
                )
                plotWaterConsumptionStats(
                    data.y_tank,
                    data.y_city,
                    data.y_well,
                    timestepSelect.options[timestepSelect.selectedIndex].text,
                    periodSelect.options[periodSelect.selectedIndex].text,
                )
                let csv = "date,puits (L),cuve (L),ville (L)\r\n"
                for (let i = 0; i < data.x_tank.length; i++) {
                    csv += (
                        data.x_tank[i] + "," + data.y_well[i] + "," + data.y_tank[i] + "," +
                        data.y_city[i] + "\r\n"
                    )
                }
                buildDownloadLink(downloadWaterConsumption, "consommation_eau", period, timestep, csv)
            }
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
    hideError("power_consumption_wrapper");

    var periodSelect = document.getElementById("period-power-consumption")
    var period = periodSelect.value
    var timestep = document.getElementById("timestep-power-consumption").value
    var unit = document.getElementById("unit-power-consumption").value

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            loaderPowerConsumption.style.visibility = "hidden"
            if (this.status != 200) {
                displayError("power_consumption_wrapper");
            } else {
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
                    unit,
                    data.x_min,
                    data.x_max,
                )
                plotPowerConsumptionStats(
                    data.pump_in,
                    data.pump_out,
                    data.city,
                    unit,
                    periodSelect.options[periodSelect.selectedIndex].text
                )
                let csv = "date,puits (" + unit + "),cuve (" + unit + "),ville (" + unit + ")\r\n"
                for (let i = 0; i < data.dates.length; i++) {
                    csv += (
                        data.dates[i] + "," + data.pump_in[i] + "," + data.pump_out[i] + "," + data.city[i]
                        + "\r\n"
                    )
                }
                buildDownloadLink(downloaderPowerConsumption, "consommation_electrique", period, timestep, csv)
            }
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

function plotTankLevelPlot(x, y, xMin, xMax) {
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
            margin: {t: 10, r: 60},
            height: 300,
            xaxis: {
                fixedrange: true,
                showline: true,
                zeroline: false,
                range: [xMin, xMax],
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

function plotWellPumpEfficiency(dates, eff, xMin, xMax) {
    Plotly.newPlot(
        document.getElementById("well_pump_efficiency_plot"),
        [{
            type: "bar",
            x: dates,
            y: eff,
            name: "Puits",
            mode: "lines",
            hoverinfo: "x+y",
            marker: { color: WELL_COLOR },
        }],
        {
            barmode: "relative",
            margin: {t: 10, r: 60},
            xaxis: {
                showline: true,
                zeroline: false,
                title: "Heure de début",
                range: [xMin, xMax],
            },
            yaxis: {
                title: "Rendement (L/kWh)",
                showline: true,
                zeroline: false,
                fixedrange: true,
            }
        }
    )
}

function updateTankLevelPlot() {
    loaderTankLevel.style.display = "block"
    hideError("tank_level_wrapper");

    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            loaderTankLevel.style.display = "none"
            if (this.status != 200) {
                displayError("tank_level_wrapper");
            } else {
                let data = JSON.parse(xhttp.responseText)
                plotTankLevelPlot(data.dates, data.volumes, data.x_min, data.x_max)
            }
        }
    }
    xhttp.open("GET", TANK_LEVEL_URL, true)
    xhttp.send()
}

function updateWellPumpEfficiencyPlot() {
    loaderWellPumpEfficiency.style.visibility = "visible"
    hideError("well_pump_efficiency_wrapper");

    var dates, volumeData, powerData, xMin, xMax
    var period = document.getElementById("period-well-pump-efficiency").value
    var timestep = document.getElementById("timestep-well-pump-efficiency").value

    function update() {
        if (!dates || !volumeData || !powerData) return
        let eff = []
        for (let i = 0; i < powerData.length; i++) {
            if (!powerData[i]) {
                eff.push(0)
            } else {
                eff.push(volumeData[i] / powerData[i])
            }
        }
        plotWellPumpEfficiency(dates, eff, xMin, xMax)
    }

    var xhttpVolume = new XMLHttpRequest();
    xhttpVolume.onreadystatechange = function() {
        if (this.readyState == 4) {
            loaderWellPumpEfficiency.style.visibility = "hidden"
            if (this.status != 200) {
                displayError("well_pump_efficiency_wrapper");
            } else {
                volumeData = JSON.parse(xhttpVolume.responseText).y_well
                update()
            }
        }
    }
    xhttpVolume.open(
        "GET",
        WATER_CONSUMPTION_URL + "?days=" + encodeURIComponent(period) + "&timestep=" + encodeURIComponent(timestep),
        true
    )
    xhttpVolume.send()
    
    var xhttpPower = new XMLHttpRequest();
    xhttpPower.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(xhttpPower.responseText)
            dates = data.dates
            xMin = data.x_min
            xMax = data.x_max
            powerData = data.pump_in.map(x => x / 60.0 * PUMP_IN_POWER / 1000.0)
            update()
        }
    }
    xhttpPower.open(
        "GET",
        POWER_CONSUMPTION_URL + "?days=" + encodeURIComponent(period) + "&timestep=" + encodeURIComponent(timestep),
        true
    )
    xhttpPower.send()
}

document.getElementById("period-water-consumption").addEventListener("change", updateWaterConsumptionPlot)
document.getElementById("timestep-water-consumption").addEventListener("change", updateWaterConsumptionPlot)
document.getElementById("period-power-consumption").addEventListener("change", updatePowerConsumptionPlot)
document.getElementById("timestep-power-consumption").addEventListener("change", updatePowerConsumptionPlot)
document.getElementById("unit-power-consumption").addEventListener("change", updatePowerConsumptionPlot)
document.getElementById("period-well-pump-efficiency").addEventListener("change", updateWellPumpEfficiencyPlot)
document.getElementById("timestep-well-pump-efficiency").addEventListener("change", updateWellPumpEfficiencyPlot)

updateWaterConsumptionPlot()
updateTankLevelPlot()
updatePowerConsumptionPlot()
updateWellPumpEfficiencyPlot()
