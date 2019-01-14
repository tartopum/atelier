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
        let xDelta = _w(5)
        let yStep = h / maxVolume
        for (var i = volumeScaleStep; i < maxVolume; i += volumeScaleStep) {
            let y = yTop + h - i * yStep
            let tick = rc.line(x - xDelta, y, x + xDelta, y, {
                roughness: 0.5,
                strokeWidth: 2
            })
            svg.appendChild(tick)
            drawLabel(x - xDelta - _w(15), y, i)
        }
    }

    function drawTank(x, waterVolumeRatio, empty, full) {
        let w = _w(150),
            y = _y(50),
            h = _h(340)
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

    function drawPump(xCenter, yCenter, isOn, isBlocked) {
        let bg = "white"
        if (isBlocked) bg = "rgb(255, 105, 97)"
        let pump = rc.circle(xCenter, yCenter, pumpDiameter, {
            roughness: 0,
            strokeWidth,
            fill: bg,
            fillStyle: "solid"
        })

        svg.appendChild(pump)

        drawLabel(xCenter + _w(2), yCenter + _h(3), "P", _h(40), true)
        if (isOn) drawPumpVibs(xCenter, yCenter)

        return {
            xLeft: xCenter - pumpDiameter / 2.0,
            xRight: xCenter + pumpDiameter / 2.0,
            xMiddle: xCenter,
            yTop: yCenter - pumpDiameter / 2.0,
            yBottom: yCenter + pumpDiameter / 2.0,
            yMiddle: yCenter,
        }
    }

    function drawFilter(xCenter, yCenter, full, blocked) {
        let yTop = yCenter - hFilter / 2.0
        let xLeft = xCenter - wFilter / 2.0
        let filter = rc.rectangle(xLeft, yTop, wFilter, hFilter, {
            roughness: 0,
            strokeWidth,
            fill: full ? waterColor : "white",
            fillStyle: "solid"
        })
        svg.appendChild(filter)
        drawLabel(xCenter, yTop - _h(10), "Filtre", _h(14), true)
    
        let coords = {
            xLeft: xLeft,
            xRight: xLeft + wFilter,
            yTop: yTop,
            yBottom: yTop + hFilter,
        }

        if (!blocked) {
            return coords
        }

        let dust = rc.rectangle(xLeft, yTop, wFilter, hFilter, {
            roughness: 1,
            strokeWidth: 1,
            fill: "black",
            fillStyle: "dots",
            fillWeight: 1
        })
        svg.appendChild(dust)

        return coords
    }

    function drawFlowmeter(x, y, yArrow, val) {
        const xMiddle = x + wFlowmeter / 2.0
        const yMiddle = y + hFlowmeter / 2.0
        let flowMeter = rc.rectangle(x, y, wFlowmeter, hFlowmeter, {
            fill: "white",
            fillStyle: "solid",
        })

        let text = document.createElementNS("http://www.w3.org/2000/svg", "text")
        text.setAttributeNS(null, "font-family", "Courier")
        text.setAttributeNS(null, "font-size", "25px")
        text.setAttributeNS(null, "dominant-baseline", "middle")
        text.setAttributeNS(null, "text-anchor", "middle")
        text.setAttributeNS(null, "x", xMiddle)
        text.setAttributeNS(null, "y", yMiddle)

        val = parseInt(val)
        val = (val > 9) ? val : "0" + val
        var textNode = document.createTextNode(val + " L/m")
        text.appendChild(textNode)

        let g = document.createElementNS("http://www.w3.org/2000/svg", "g")
        g.appendChild(text)

        let arrow = rc.line(xMiddle, y + hFlowmeter, xMiddle, yArrow, {
            roughness: 0
        })

        svg.appendChild(arrow)
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

    function drawLabel(x, yMiddle, text, fontSize = 16, centerY = false) {
        let txt = document.createElementNS("http://www.w3.org/2000/svg", "text")
        txt.setAttributeNS(null, "font-family", "Slabo")
        txt.setAttributeNS(null, "font-weight", "bold")
        txt.setAttributeNS(null, "font-size", fontSize + "px")
        txt.setAttributeNS(null, "dominant-baseline", "middle")
        if (centerY) txt.setAttributeNS(null, "text-anchor", "middle")
        txt.setAttributeNS(null, "x", x)
        txt.setAttributeNS(null, "y", yMiddle)

        var textNode = document.createTextNode(text)
        txt.appendChild(textNode)
        
        let g = document.createElementNS("http://www.w3.org/2000/svg", "g")
        g.appendChild(txt)

        svg.appendChild(g)
        let bbox = g.getBBox()

        return {
            xLeft: bbox.x,
            xRight: bbox.x + bbox.width,
            yTop: bbox.y,
            yBottom: bbox.y + bbox.height,
        }
    }

    function drawWaterVolumeSensor(tank, yRatio, activated) {
        let w = _w(10)
        let y = tank.yBottom - yRatio * (tank.yBottom - tank.yTop)
        let tick = rc.line(tank.xLeft, y, tank.xRight, y, {
            roughness: 0.5,
            strokeWidth: 1
        })
        svg.appendChild(tick)

        if (!activated) return

        let x1 = tank.xLeft - _w(5)
        for (let i = -1; i < 2; i++) {
            let x2 = x1 - (i == 0 ? _w(8) : _w(5))
            let y1 = y + i * _h(5)
            let y2 = y1 + i * _h(3)
            let tick = rc.line(x1, y1, x2, y2, {
                roughness: 1,
                strokeWidth: 1
            })
            svg.appendChild(tick)
        }
    }
    
    const pipeWidth = _h(15)
    const yFlowmeter = _y(250)
    const wFlowmeter = _w(100)
    const hFlowmeter = _h(50)
    const pumpDiameter = _h(60)
    const wFilter = _w(50)
    const hFilter = 1.5 * pipeWidth

    let tank = drawTank(_x(500), state.water_level, state.is_tank_empty, state.is_tank_full)

    const xTankTopGate = tank.xLeft + _w(20)
    if (state.flow_in) {
        drawFallingWater(tank);
    }
    let pipeH1 = drawHPipe(
        _x(50),
        tank.xLeft - _w(160),
        tank.yBottom - pipeWidth - _h(4),
        state.flow_in > 0
    )
    let pipeV2 = drawVPipe(
        xTankTopGate,
        tank.yTop - _h(20),
        _h(22),
        state.flow_in > 0
    )
    let pipeV1 = drawVPipe(
        pipeH1.xRight,
        pipeV2.yTop,
        pipeH1.yTop - pipeV2.yTop,
        state.flow_in > 0
    )
    elbow(
        pipeH1.xRight,
        pipeH1.yTop,
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
    let pipeH2 = drawHPipe(
        pipeV1.xRight,
        pipeV2.xLeft - pipeV1.xRight,
        pipeV2.yTop - pipeWidth,
        state.flow_in
    )
    elbow(
        pipeH2.xRight,
        pipeH2.yBottom,
        3 * Math.PI / 2,
        2 * Math.PI,
        state.flow_in
    )
    let pipeOutH1 = drawHPipe(
        tank.xRight - _w(3),
        _w(75),
        pipeH1.yTop,
        true
    )
    let pipeOutH2 = drawHPipe(
        pipeOutH1.xRight,
        _w(80),
        pipeH1.yTop,
        state.pump_out
    )
    let pipeOutH3 = drawHPipe(
        pipeOutH2.xRight - _w(2),
        _x(950) - pipeOutH2.xRight,
        pipeH1.yTop,
        state.urban_network || state.pump_out
    )

    let pumpIn = drawPump(
        _x(100),
        pipeH1.yMiddle,
        state.pump_in,
        state.is_motor_in_blocked,
    )
    let pumpOut = drawPump(
        pipeOutH1.xRight,
        pipeOutH1.yMiddle,
        state.pump_out,
        state.is_motor_out_blocked,
    )
    let filter = drawFilter(
        tank.xLeft - _w(280),
        pipeOutH1.yMiddle,
        state.flow_in,
        state.is_filter_in_blocked
    )

    let flowmeterIn = drawFlowmeter(
        tank.xLeft - _w(240),
        yFlowmeter,
        pipeH1.yTop,
        state.flow_in
    )
    let flowmeterOut = drawFlowmeter(
        tank.xRight + _w(200),
        yFlowmeter,
        pipeOutH1.yTop,
        state.flow_out
    )
    let pipeUrbanV = drawVPipe(
        pipeOutH2.xRight - pipeWidth,
        _h(200),
        pipeOutH1.yTop - _h(198),
        state.urban_network
    )
    drawUrbanConnection(pipeUrbanV.xRight, pipeOutH3.yTop, state.urban_network)
    drawLabel(_x(0), pipeH1.yMiddle, "Puits")
    drawLabel(pipeOutH3.xRight + _w(10), pipeOutH1.yMiddle, "Ferme")
    let urbanLabel = drawLabel(pipeUrbanV.xMiddle, pipeUrbanV.yTop - _h(20), "Ville", 16, true)

    drawWaterVolumeSensor(tank, lowSensorRelPos, !state.is_tank_empty)
    drawWaterVolumeSensor(tank, highSensorRelPos, state.is_tank_full)

    if (!state.manual_mode) {
        drawLabel(_x(0), _y(20), "Cliquer sur la pompe du puits pour la commander.")
    }
    
    if (!state.is_motor_in_blocked) {
        addLink(
            pumpIn.xLeft,
            pumpIn.yTop,
            pumpIn.xRight - pumpIn.xLeft,
            pumpIn.yBottom - pumpIn.yTop,
            state.pump_in ? links.pumpInOff : links.pumpInOn,
            state.manual_mode
        )
    }
    if (!state.is_motor_out_blocked && state.manual_mode) {
        addLink(
            pumpOut.xLeft,
            pumpOut.yTop,
            pumpOut.xRight - pumpOut.xLeft,
            pumpOut.yBottom - pumpOut.yTop,
            state.pump_out ? links.pumpOutOff : links.pumpOutOn,
            state.manual_mode
        )
    }
    if (state.manual_mode) {
        addLink(
            urbanLabel.xLeft,
            urbanLabel.yTop,
            urbanLabel.xRight - urbanLabel.xLeft,
            urbanLabel.yBottom - urbanLabel.yTop,
            state.urban_network ? links.urbanNetworkOff : links.urbanNetworkOn,
            state.manual_mode
        )
    }
    if (!state.manual_mode) {
        addLink(
            filter.xLeft,
            filter.yTop,
            filter.xRight - filter.xLeft,
            filter.yBottom - filter.yTop,
            links.filterCleaningOn,
            state.manual_mode
        )
    } else {
        addLink(
            filter.xLeft,
            filter.yTop,
            filter.xRight - filter.xLeft,
            filter.yBottom - filter.yTop,
            state.filter_cleaning ? links.filterCleaningOff : links.filterCleaningOn,
            state.manual_mode
        )
    }
};
