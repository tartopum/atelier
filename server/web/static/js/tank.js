var Tank = function(svg, state, links) {

    const maxVolume = 5 // m3
    const volumeScaleStep = 1
    const lowSensorRelPos = 0.35 / 5
    const highSensorRelPos = 4.8 / maxVolume
    const padding = 5
    const _widthRef = 1000 + 2 * padding
    const _heightRef = 400 + 2 * padding
    var _width = parseInt(svg.parentNode.style.width),
        _height = parseInt(svg.parentNode.style.height)

    svg.setAttribute("width", _width + "px")
    svg.setAttribute("height", _height + "px")

    const roughness = 0.5
    const strokeWidth = 2
    const rc = rough.svg(svg)
    const innerWight = _width - 2 * padding
    const innerHeight = _height - 2 * padding
    const waterColor = "rgb(127, 127, 255)"

    function _w(w) {
        return (w / _widthRef) * innerWight
    }

    function _x(x) {
        return _w(x) + padding
    }

    function _h(h) {
        return (h / _heightRef) * innerHeight
    }

    function _y(y) {
        return _h(y) + padding
    }

    function addLink(x, y, w, h, href, showBorder) {
        let padding = _w(5)
        var rect = rc.rectangle(x - padding, y - padding, w + 2 * padding, h + 2 * padding, {
            roughness: 0.5,
            strokeWidth: showBorder ? 2 : 0,
            stroke: "rgb(255, 105, 97)",
            fill: "rgba(0, 0, 0, 0)",
            fillStyle: "solid",
        })
        var link = document.createElementNS("http://www.w3.org/2000/svg", "a")
        link.setAttributeNS(null, "href", href)
        link.appendChild(rect)
        svg.appendChild(link)
    }

    function drawWater(x, y, w, h, roughness = 0) {
        let water = rc.rectangle(x, y, w, h, {
            fill: waterColor,
            fillStyle: "solid",
            roughness: roughness,
            strokeWidth: 0
        })
        svg.appendChild(water)
    }

    function drawTankVolumeScale(x, yTop, h) {
        let xDelta = _w(10)
        let yStep = h / maxVolume
        for (var i = 0; i < maxVolume; i += volumeScaleStep) {
            if (i > 0) {
                let y = yTop + h - i * yStep
                let tick = rc.line(x - xDelta, y, x, y, {
                    roughness: 0.5,
                    strokeWidth: 2
                })
                svg.appendChild(tick)
                drawLabel(x - xDelta - _w(40), y, i * 1000)
            }

            for (let p of [0.25, 0.5, 0.75]) {
                let y = yTop + h - (i + p) * yStep
                let tick = rc.line(x - _w(5), y, x, y, {
                    roughness: 0.5,
                    strokeWidth: 1
                })
                svg.appendChild(tick)
            }
        }
    }

    function drawTank(x, waterVolumeRatio, empty, full) {
        let w = _w(150),
            y = _y(50),
            h = _h(310)
        let yWater

        if (empty) {
            yWater = (y + h) - h * lowSensorRelPos + _h(7)
        } else if(full) {
            yWater = (y + h) - h * highSensorRelPos - _h(2)
        } else {
            let highPos = (y + h) - h * highSensorRelPos
            let lowPos = (y + h) - h * lowSensorRelPos 
            yWater = lowPos - (lowPos - highPos) * waterVolumeRatio
        }

        let tank = rc.rectangle(x, y, w, h, {
            roughness: 0.5,
            strokeWidth: 2,
        })
        drawWater(
            x,
            yWater,
            w,
            (y + h) - yWater
        )

        // Draw waves
        let wavePts = []
        let nPoints = 20
        for (let i = 0; i < nPoints; i++) {
            let xWave = (w / (nPoints - 1)) * i + x;
            let xdeg = (Math.PI / 100) * xWave;
            let yWave = Math.round(Math.sin(xdeg)) + yWater;
            wavePts.push([xWave, yWave]);
        }
        let wave = rc.curve(wavePts, {
          stroke: waterColor, strokeWidth: 6, roughness: 0.8
        });
        svg.appendChild(wave)
        
        svg.appendChild(tank)

        drawTankVolumeScale(x, y, h)

        return {
            xLeft: x,
            xRight: x + w,
            yTop: y,
            yBottom: y + h
        };
    }

    function drawPumpVibs(x, y) {
        let angleProps = [0.3, 0.1]
        for (let i = 0; i < angleProps.length; i++) {
            let angleLen = angleProps[i] * Math.PI / 2.0
            let style = { roughness: 0, strokeWidth: 2 }
            let diameter = pumpDiameter + _w(15) + i * _w(10)

            for (var j = 0; j < 4; j++) {
                let start = j * Math.PI / 2.0
                let angleMargin = (Math.PI / 2.0 - angleLen) / 2.0 

                let vib = rc.arc(
                    x,
                    y,
                    diameter,
                    diameter,
                    start + angleMargin,
                    start + angleMargin + angleLen,
                    false,
                    style
                )
                svg.appendChild(vib)
            }
        }
    }

    function drawPump(xCenter, yCenter, isOn, isDeactivated, link) {
        let bg = "white"
        if (isDeactivated) bg = "rgb(255, 105, 97)"
        let pump = rc.circle(xCenter, yCenter, pumpDiameter, {
            roughness: 0,
            strokeWidth,
            fill: bg,
            fillStyle: "solid"
        })

        svg.appendChild(pump)

        drawLabel(xCenter + _w(2), yCenter + _h(3), "P", _h(40), true)
        if (isDeactivated) {
            drawLabel(xCenter, yCenter - pumpDiameter / 2.0 - _y(10), "Désactivée", 14, true, link)
        } else if (isOn) {
            drawPumpVibs(xCenter, yCenter)
            drawLabel(xCenter, yCenter - pumpDiameter / 2.0 - _y(20), "Allumée", 14, true, link)
        } else {
            drawLabel(xCenter, yCenter - pumpDiameter / 2.0 - _y(10), "Éteinte", 14, true, link)
        }

        var coords = {
            xLeft: xCenter - pumpDiameter / 2.0,
            xRight: xCenter + pumpDiameter / 2.0,
            xMiddle: xCenter,
            yTop: yCenter - pumpDiameter / 2.0,
            yBottom: yCenter + pumpDiameter / 2.0,
            yMiddle: yCenter,
        }

        if (link) {
            addLink(
                coords.xLeft,
                coords.yTop,
                coords.xRight - coords.xLeft,
                coords.yBottom - coords.yTop,
                link
            )
        }

        return coords
    }

    function drawFilter(xCenter, yCenter, full, blocked, open) {
        let yTop = yCenter - hFilter / 2.0
        let xLeft = xCenter - wFilter / 2.0
        let filter = rc.rectangle(xLeft, yTop, wFilter, hFilter, {
            roughness: 0,
            strokeWidth,
            fill: full ? waterColor : "white",
            fillStyle: "solid"
        })
        svg.appendChild(filter)

        let link = links.filterCleaningOn
        if (state.manual_mode) {
            link = state.filter_cleaning ? links.filterCleaningOff : links.filterCleaningOn
        }
        let label = "Filtre fermé"
        if (blocked) label = "Filtre encrassé"
        else if (open) label = "Filtre ouvert"
        drawLabel(xCenter, yTop - _h(15), label, 14, true, link)
    
        let coords = {
            xLeft: xLeft,
            xRight: xLeft + wFilter,
            xMiddle: xLeft + wFilter / 2.0,
            yTop: yTop,
            yBottom: yTop + hFilter,
            yMiddle: yTop + hFilter / 2.0,
        }

        if (blocked) {
            let dust = rc.rectangle(xLeft, yTop, wFilter, hFilter, {
                roughness: 1,
                strokeWidth: 1,
                fill: "black",
                fillStyle: "dots",
                fillWeight: 1
            })
            svg.appendChild(dust)
        }
        
        if (open) {
            let wOpening = _w(8)
            let hOpening = _h(10)
            let xOpening = coords.xMiddle - wOpening / 2.0

            if (full) {
                drawWater(xOpening, coords.yBottom - _h(2), wOpening, hOpening)
            } else {
                svg.appendChild(rc.rectangle(xOpening, coords.yBottom - _h(2), wOpening, hOpening, {
                    roughness: 0,
                    strokeWidth: 0,
                    fill: "white",
                    fillStyle: "solid",
                }))
            }

            svg.appendChild(rc.line(xOpening, coords.yBottom, xOpening, coords.yBottom + hOpening, {
                roughness: 0,
                strokeWidth: 2
            }))
            svg.appendChild(rc.line(xOpening + wOpening, coords.yBottom, xOpening + wOpening, coords.yBottom + hOpening, {
                roughness: 0,
                strokeWidth: 2
            }))
        }

        addLink(
            coords.xLeft,
            coords.yTop,
            coords.xRight - coords.xLeft,
            coords.yBottom - coords.yTop,
            link
        )

        return coords
    }
    
    function drawPressureSensor(xCenter, yCenter, activated) {
        let diameter = 3 * pipeWidth
        let sensor = rc.circle(xCenter, yCenter, diameter, {
            roughness: 0,
            strokeWidth,
            fill: activated ? "rgb(255, 105, 97)" : "white",
            fillStyle: "solid"
        })
        svg.appendChild(sensor)
        
        let center = rc.circle(xCenter, yCenter, _w(5), {
            roughness: 0,
            strokeWidth,
            fill: "black",
            fillStyle: "solid"
        })
        svg.appendChild(center)
        
        let padding = _w(5)
        let arcDiameter = diameter - 2 * padding 
        let arc = rc.arc(xCenter, yCenter, arcDiameter, arcDiameter, 0.75 * Math.PI, 2.25 * Math.PI, false, {
            roughness: 0,
            strokeWidth: 1,
        })
        svg.appendChild(arc)

        let coords = {
            xLeft: xCenter - diameter / 2.0,
            xRight: xCenter + diameter / 2.0,
            xMiddle: xCenter,
            yTop: yCenter - diameter / 2.0,
            yBottom: yCenter + diameter / 2.0,
            yMiddle: yCenter,
        }

        let hand
        if (activated) {
            hand = rc.line(xCenter - _w(7), yCenter, coords.xRight - padding / 2.0, yCenter,  {
                roughness: 0,
                strokeWidth: 2
            })
        } else {
            hand = rc.line(xCenter + _w(7), yCenter, coords.xLeft + padding / 2.0, yCenter,  {
                roughness: 0,
                strokeWidth: 2
            })
        }
        svg.appendChild(hand)

        let label = activated ? "Surpression" : "Pression normale"
        drawLabel(xCenter, coords.yTop - _h(15), label, 14, true)
    
        return coords
    }

    function drawFlowmeter(x, y, val) {
        const xMiddle = x + wFlowmeter / 2.0
        const yMiddle = y + hFlowmeter / 2.0
        let flowMeter = rc.rectangle(x, y, wFlowmeter, hFlowmeter, {
            fill: "white",
            fillStyle: "solid",
        })

        let text = document.createElementNS("http://www.w3.org/2000/svg", "text")
        text.setAttributeNS(null, "font-family", "Courier")
        text.setAttributeNS(null, "font-size", "20px")
        text.setAttributeNS(null, "dominant-baseline", "middle")
        text.setAttributeNS(null, "text-anchor", "end")
        text.setAttributeNS(null, "x", xMiddle - _w(2))
        text.setAttributeNS(null, "y", yMiddle)

        val = parseInt(val)
        var textNode = document.createTextNode(val)
        text.appendChild(textNode)

        let g = document.createElementNS("http://www.w3.org/2000/svg", "g")
        g.appendChild(text)
        
        text = document.createElementNS("http://www.w3.org/2000/svg", "text")
        text.setAttributeNS(null, "font-family", "Courier")
        text.setAttributeNS(null, "font-size", "14px")
        text.setAttributeNS(null, "dominant-baseline", "middle")
        text.setAttributeNS(null, "text-anchor", "start")
        text.setAttributeNS(null, "x", xMiddle + _w(2))
        text.setAttributeNS(null, "y", yMiddle)

        textNode = document.createTextNode("L/m")
        text.appendChild(textNode)
        g.appendChild(text)

        svg.appendChild(flowMeter)
        svg.appendChild(g)

        return {
            xLeft: x,
            xRight: x + wFlowmeter,
            xMiddle,
            yTop: y,
            yBottom: y + hFlowmeter,
            yMiddle
        }
    }

    function drawHPipe(xLeft, w, yTop, full) {
        let yBottom = yTop + pipeWidth
        let xRight = xLeft + w

        let topLine = rc.line(xLeft, yTop, xRight, yTop, {
            roughness: 0,
            strokeWidth
        })
        let bottomLine = rc.line(xLeft, yBottom, xRight, yBottom, {
            roughness: 0,
            strokeWidth
        })

        if (full) {
            drawWater(xLeft, yTop, xRight - xLeft, yBottom - yTop)
        }

        svg.appendChild(topLine)
        svg.appendChild(bottomLine)

        return {
            xLeft,
            xRight,
            xMiddle: (xLeft + xRight) / 2.0,
            yTop,
            yBottom,
            yMiddle: (yTop + yBottom) / 2.0,
        }
    }
    
    function drawVPipe(xLeft, yTop, h, full) {
        let xRight = xLeft + pipeWidth
        let yBottom = yTop + h

        let leftLine = rc.line(xLeft, yTop, xLeft, yBottom, {
            roughness: 0,
            strokeWidth
        })
        let rightLine = rc.line(xRight, yTop, xRight, yBottom, {
            roughness: 0,
            strokeWidth
        })
        
        if (full) {
            drawWater(xLeft, yTop, xRight - xLeft, yBottom - yTop)
        }

        svg.appendChild(leftLine)
        svg.appendChild(rightLine)
        
        return {
            xLeft,
            xRight,
            xMiddle: (xLeft + xRight) / 2.0,
            yTop,
            yBottom,
            yMiddle: (yTop + yBottom) / 2.0,
        }
    }

    function elbow(x, y, angleStart, angleEnd, full) {
        // To fill the blank when there is water
        let angleDelta = 0.1
        if (full) {
            let water = rc.arc(
                x,
                y,
                2 * pipeWidth,
                2 * pipeWidth,
                angleStart - angleDelta,
                angleEnd + angleDelta,
                true,
                {
                    roughness: 0,
                    strokeWidth: 0,
                    fill: waterColor,
                    fillStyle: "solid",
                }
            )
            svg.appendChild(water)
        }
        let arc = rc.arc(
            x,
            y,
            2 * pipeWidth,
            2 * pipeWidth,
            angleStart - angleDelta,
            angleEnd + angleDelta,
            false,
            { roughness: 0, strokeWidth }
        )
        svg.appendChild(arc)
    }

    function drawTankWaterBorder(tank, xPipe, waterVolumeRatio) {
        let yWater = tank.yBottom - waterVolumeRatio * (tank.yBottom - tank.yTop)
        let roughness = 0.5;
        if (!state.flow_in) {
            let line = rc.line(tank.xLeft, yWater, tank.xRight, yWater, { roughness });
            svg.appendChild(line);
            return;
        }
        let pathLeft = rc.path((
            "M" + tank.xLeft + " " + yWater +
            " H" + xPipe +
            " V" + tank.yTop
        ), { roughness });
        let pathRight = rc.path((
            "M" + (xPipe + pipeWidth) + " " + tank.yTop +
            "V" + yWater +
            "H" + tank.xRight
        ), { roughness: 0.5 });

        svg.appendChild(pathLeft);
        svg.appendChild(pathRight);
    }

    function drawFallingWater(tank) {
        drawWater(
            xTankTopGate,
            tank.yTop - _h(5),
            pipeWidth,
            tank.yBottom - tank.yTop - _h(5)
        );
    }

    function drawUrbanConnection(x, y, urbanOn) {
        if (!urbanOn) return
        elbow(
            x,
            y,
            Math.PI / 2.0,
            Math.PI,
            true
        )
    }

    function drawLabel(x, yMiddle, text, fontSize = 16, centerX = false, link = false) {
        let txt = document.createElementNS("http://www.w3.org/2000/svg", "text")
        txt.setAttributeNS(null, "font-family", "Slabo")
        txt.setAttributeNS(null, "font-weight", "bold")
        txt.setAttributeNS(null, "font-size", fontSize + "px")
        txt.setAttributeNS(null, "dominant-baseline", "middle")
        if (centerX) txt.setAttributeNS(null, "text-anchor", "middle")
        txt.setAttributeNS(null, "x", x)
        txt.setAttributeNS(null, "y", yMiddle)

        var textNode = document.createTextNode(text)
        txt.appendChild(textNode)
        
        let g = document.createElementNS("http://www.w3.org/2000/svg", "g")
        g.appendChild(txt)

        svg.appendChild(g)
        let bbox = g.getBBox()

        var coords = {
            xLeft: bbox.x,
            xRight: bbox.x + bbox.width,
            yTop: bbox.y,
            yBottom: bbox.y + bbox.height,
        }

        if (link) {
            txt.setAttributeNS(null, "text-decoration", "underline")
            txt.setAttributeNS(null, "fill", "#8e44b4")
            addLink(
                coords.xLeft,
                coords.yTop,
                coords.xRight - coords.xLeft,
                coords.yBottom - coords.yTop,
                link
            )
        }

        return coords
    }

    function drawWaterVolumeSensor(tank, yRatio, activated) {
        let w = _w(10)
        let y = tank.yBottom - yRatio * (tank.yBottom - tank.yTop)
        let tick = rc.line(tank.xLeft, y, tank.xRight, y, {
            roughness: 0.5,
            strokeWidth: 1,
            stroke: activated ? "black" : "rgba(0, 0, 0, 0.2)",
        })
        svg.appendChild(tick)
    }
    
    const pipeWidth = _h(15)
    const yFlowmeter = _y(250)
    const wFlowmeter = _w(70)
    const hFlowmeter = _h(40)
    const pumpDiameter = _h(60)
    const wFilter = _w(50)
    const hFilter = 1.5 * pipeWidth

    let tank = drawTank(_x(450), state.water_level, state.is_tank_empty, state.is_tank_full)

    const xTankTopGate = tank.xLeft + _w(20)
    if (state.flow_in) {
        drawFallingWater(tank);
    }
    let pipeH1 = drawHPipe(
        _x(30),
        tank.xLeft - _w(310),
        tank.yBottom - pipeWidth - _h(4),
        state.pump_in
    )
    let pipeVWell = drawVPipe(
        pipeH1.xLeft - pipeWidth,
        pipeH1.yBottom,
        _h(30),
        state.pump_in
    )
    elbow(
        pipeH1.xLeft,
        pipeH1.yBottom,
        Math.PI,
        3/2 * Math.PI,
        state.pump_in
    )
    let pipeH2 = drawHPipe(
        pipeH1.xRight,
        tank.xLeft - _w(80) - pipeH1.xRight,
        pipeH1.yTop,
        state.flow_in > 0
    )
    let filter = drawFilter(
        pipeH1.xRight + _w(20),
        pipeH1.yMiddle,
        state.pump_in,
        state.is_filter_in_blocked,
        state.filter_cleaning
    )
    let pipeV2 = drawVPipe(
        xTankTopGate,
        tank.yTop - _h(20),
        _h(22),
        state.flow_in > 0
    )
    let pipeV1 = drawVPipe(
        pipeH2.xRight,
        pipeV2.yTop,
        pipeH1.yTop - pipeV2.yTop,
        state.flow_in > 0
    )
    elbow(
        pipeH2.xRight,
        pipeH2.yTop,
        0,
        Math.PI / 2,
        state.flow_in
    )
    elbow(
        pipeV1.xRight,
        pipeV1.yTop,
        Math.PI,
        3 * Math.PI / 2,
        state.flow_in
    )
    let pipeH3 = drawHPipe(
        pipeV1.xRight,
        pipeV2.xLeft - pipeV1.xRight,
        pipeV2.yTop - pipeWidth,
        state.flow_in
    )
    elbow(
        pipeH3.xRight,
        pipeH3.yBottom,
        3 * Math.PI / 2,
        2 * Math.PI,
        state.flow_in
    )
    let pipeOutH1 = drawHPipe(
        tank.xRight - _w(3),
        _w(50),
        pipeH1.yTop,
        true
    )
    let pipeOutH2 = drawHPipe(
        pipeOutH1.xRight,
        _w(180),
        pipeH1.yTop,
        state.pump_out
    )
    let pipeOutH3 = drawHPipe(
        pipeOutH2.xRight - _w(2),
        _x(950) - pipeOutH2.xRight,
        pipeH1.yTop,
        state.urban_network || state.pump_out
    )

    let pumpInLink = state.pump_in ? links.pumpInOff : links.pumpInOn
    if (!state.pump_in_activated) {
        pumpInLink = links.activatePumpIn
    }
    let pumpIn = drawPump(
        _x(90),
        pipeH1.yMiddle,
        state.pump_in,
        !state.pump_in_activated,
        pumpInLink
    )

    let pumpOutLink = null
    if (state.pump_out_activated && state.manual_mode) {
        pumpOutLink = state.pump_out ? links.pumpOutOff : links.pumpOutOn
    } else if (!state.pump_out_activated) {
        pumpOutLink = links.activatePumpOut
    }
    let pumpOut = drawPump(
        pipeOutH1.xRight,
        pipeOutH1.yMiddle,
        state.pump_out,
        !state.pump_out_activated,
        pumpOutLink
    )

    let flowmeterIn = drawFlowmeter(
        tank.xLeft - _w(180),
        pipeH2.yMiddle - hFlowmeter / 2.0,
        state.flow_in
    )
    let flowmeterOut = drawFlowmeter(
        tank.xRight + _w(250),
        pipeOutH3.yMiddle - hFlowmeter / 2.0,
        state.flow_out
    )
    let pipeUrbanV = drawVPipe(
        pipeOutH2.xRight - pipeWidth,
        _h(200),
        pipeOutH1.yTop - _h(198),
        state.urban_network
    )
    drawUrbanConnection(pipeUrbanV.xRight, pipeOutH3.yTop, state.urban_network)
    drawLabel(pipeVWell.xLeft - _w(8), pipeVWell.yBottom + _h(15), "Puits")

    let urbanNetworkLink = null
    if (state.manual_mode) {
        urbanNetworkLink = state.urban_network ? links.urbanNetworkOff : links.urbanNetworkOn
    }
    let urbanLabel = drawLabel(
        pipeUrbanV.xMiddle,
        pipeUrbanV.yTop - _h(20),
        "Ville " + (state.urban_network ? "ouverte" : "fermée"),
        14,
        true,
        urbanNetworkLink
    )

    drawPressureSensor(tank.xRight + _w(140), pipeOutH1.yMiddle, state.is_overpressured)

    drawWaterVolumeSensor(tank, lowSensorRelPos, !state.is_tank_empty)
    drawWaterVolumeSensor(tank, highSensorRelPos, state.is_tank_full)
};
