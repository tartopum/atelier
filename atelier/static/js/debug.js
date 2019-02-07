function plotRPiDiskUsage(total, used) {
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
            width: 400,
            height: 400,
            margin: {t: 50},
            title: {
                text: "Espace disque",
                font: {
                    family: "Slabo, Helvetica, Arial, sans-serif",
                    size: 30,
                },
            },
            legend: {
                x: 0.5,
                y: 1,
                orientation: "h",
                xanchor: "center",
                yanchor: "middle",
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
