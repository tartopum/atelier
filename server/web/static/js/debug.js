var piePlotSize = Math.min(300, window.innerWidth - 40)

function plotRPiDisk(total, used) {
    total = Math.round(total / 10000000) / 100.0
    used = Math.round(used / 10000000) / 100.0
    Plotly.newPlot(
        document.getElementById("rpi_disk_usage"),
        [{
            type: "pie",
            hoverinfo: "label+value",
            hole: .6,
            values: [used, total - used],
            labels: ["Utilisé", "Libre"],
            marker: { colors: ["#ff6961", "#e9e9e9"] },
        }],
        {
            showlegend: true,
            width: piePlotSize,
            height: piePlotSize,
            margin: {t: 110, l: 50, r: 50, b: 10},
            title: {
                text: "Espace disque",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
            },
            legend: {
                x: 0,
                y: 1,
                orientation: "v",
                xanchor: "center",
                yanchor: "bottom",
            },
            annotations: [{
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 25,
                },
                showarrow: false,
                text: "Total :",
                x: 0.5,
                y: 0.6,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }, {
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 25,
                },
                showarrow: false,
                text: total + "G",
                x: 0.5,
                y: 0.45,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }]
        }
    )
}

function plotRPiCPU(percent, temp, freq) {
    freq = Math.round(freq)
    Plotly.newPlot(
        document.getElementById("rpi_cpu_usage"),
        [{
            type: "pie",
            hoverinfo: "label+value",
            hole: .6,
            values: [percent, 100 - percent],
            labels: ["Utilisé", "Libre"],
            marker: { colors: ["#ff6961", "#e9e9e9"] },
        }, {
            type: "pie",
            hoverinfo: "label+value",
            hole: .6,
            values: [percent, 100 - percent],
            labels: ["Utilisé", "Libre"],
            marker: { colors: ["#ff6961", "#e9e9e9"] },
        }],
        {
            showlegend: true,
            width: piePlotSize,
            height: piePlotSize,
            margin: {t: 110, l: 50, r: 50, b: 10},
            title: {
                text: "Processeur",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
            },
            legend: {
                x: 0,
                y: 1,
                orientation: "v",
                xanchor: "center",
                yanchor: "bottom",
            },
            annotations: [{
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 25,
                },
                showarrow: false,
                text: freq + "MHz",
                x: 0.5,
                y: 0.5,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }]
        }
    )

    if (temp !== null) {
        temp = Math.round(temp)
        let MIN_TEMP = 20
        let MID_TEMP = 60
        let HIGH_TEMP = 75 
        let MAX_TEMP = 90
        let tempBarColor = "#e9e9e9"
        let tempTitleSuffix = "normale"
        if (temp >= MID_TEMP) {
            tempBarColor = "#ffb347"
            tempTitleSuffix = "légère chauffe"
        }
        if (temp >= HIGH_TEMP) {
            tempBarColor = "#ff6961"
            tempTitleSuffix = "surchauffe !"
        }
        Plotly.newPlot(
            document.getElementById("rpi_cpu_temp"),
            [{
                type: "bar",
                y: [""],
                x: [temp],
                orientation: "h",
                marker: { color: [tempBarColor] },
                hoverinfo: "skip",
            }],
            {
                showlegend: false,
                width: piePlotSize,
                height: 100,
                margin: {t: 30, l: 50, r: 50, b: 30},
                title: {
                    text: "Température (°C)",
                    font: {
                        family: "Slabo, Helvetica, Arial, sans-serif",
                        size: 20,
                    },
                },
                xaxis: {
                    showgrid: false,
                    fixedrange: true,
                    showline: false,
                    zeroline: false,
                    range: [20, MAX_TEMP],
                    ticks: "outside",
                    dtick: 10,
                },
                yaxis: {
                    fixedrange: true,
                    showline: false,
                    zeroline: false,
                },
                annotations: [{
                    font: {
                        family: "Slabo, Helvetica, Arial, sans-serif",
                        size: 14,
                    },
                    showarrow: false,
                    text: tempTitleSuffix,
                    x: (temp - MIN_TEMP) / 2.0 + MIN_TEMP,
                    y: 0.5,
                    xanchor: "center",
                    yanchor: "middle",
                    yref: "paper",
                }]
            }
        )
    }
}

function plotRPiMemory(total, used) {
    total = Math.round(total / 10000000) / 100.0
    used = Math.round(used / 10000000) / 100.0
    Plotly.newPlot(
        document.getElementById("rpi_memory"),
        [{
            type: "pie",
            hoverinfo: "label+value",
            hole: .6,
            values: [used, total - used],
            labels: ["Utilisé", "Libre"],
            marker: { colors: ["#ff6961", "#e9e9e9"] },
        }],
        {
            showlegend: true,
            width: piePlotSize,
            height: piePlotSize,
            margin: {t: 110, l: 50, r: 50, b: 10},
            title: {
                text: "Mémoire vive",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
            },
            legend: {
                x: 0,
                y: 1,
                orientation: "v",
                xanchor: "center",
                yanchor: "bottom",
            },
            annotations: [{
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 25,
                },
                showarrow: false,
                text: "Total :",
                x: 0.5,
                y: 0.6,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }, {
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 25,
                },
                showarrow: false,
                text: total + "G",
                x: 0.5,
                y: 0.45,
                xanchor: "center",
                yanchor: "middle",
                xref: "paper",
                yref: "paper",
            }]
        }
    )
}
