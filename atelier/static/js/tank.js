var Tank = function(svg, state, links) {
    const maxVolume = 5 // m3
    const volumeScaleStep = 1
    const padding = 5
    const _widthRef = 1000 + 2 * padding
    const _heightRef = 400 + 2 * padding
    // TODO
    var _width = _widthRef,
        _height = 400
    svg.setAttribute("width", _width + "px")
    svg.setAttribute("height", _height + "px")
    svg.style.border = "1px solid #000" // TODO

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

    function wrapIntoLink(el, href) {
        var link = document.createElementNS("http://www.w3.org/2000/svg", "a")
        link.setAttributeNS(null, "href", href)
        link.appendChild(el)
        return link
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

    function drawTank(x, waterVolumeRatio) {
        let w = _w(150),
            y = _y(50),
            h = _h(340),
            yWater = y + (1 - waterVolumeRatio) * h

        let tank = rc.rectangle(x, y, w, h, {
            roughness: 0.5,
            strokeWidth: 2,
        })
        drawWater(
            x,
            yWater,
            w, waterVolumeRatio * h
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

    function drawPump(xCenter, yCenter, isOn, isBlocked, href) {
        let bg = "white"
        if (isBlocked) bg = "rgb(255, 105, 97)"
        let pump = rc.circle(xCenter, yCenter, pumpDiameter, {
            roughness: 0,
            strokeWidth,
            fill: bg,
            fillStyle: "solid"
        })

        if (href) {
            pump = wrapIntoLink(pump, href)
        }
        svg.appendChild(pump)

        drawLabel(xCenter + _w(2), yCenter + _h(3), "P", _h(40), true, href)
        if (isOn) drawPumpVibs(xCenter, yCenter)
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
        if (!blocked) return

        let dust = rc.rectangle(xLeft, yTop, wFilter, hFilter, {
            roughness: 1,
            strokeWidth: 1,
            fill: "black",
            fillStyle: "dots",
            fillWeight: 1
        })
        svg.appendChild(dust)
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
        if (!state.flowIn) {
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

    function drawUrbanConnection(x, y, pumpOutEnabled) {
        if (pumpOutEnabled) return
        elbow(
            x,
            y,
            Math.PI / 2.0,
            Math.PI,
            true
        )
    }

    function drawLabel(x, yMiddle, text, fontSize = 16, centerY = false, href = "") {
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
        
        if (href) txt = wrapIntoLink(txt, href)

        let g = document.createElementNS("http://www.w3.org/2000/svg", "g")
        g.appendChild(txt)

        svg.appendChild(g)
    }
    
    const pipeWidth = _h(15)
    const yFlowmeter = _y(250)
    const wFlowmeter = _w(100)
    const hFlowmeter = _h(50)
    const pumpDiameter = _h(60)
    const wFilter = _w(50)
    const hFilter = 1.5 * pipeWidth

    let tank = drawTank(_x(500), state.waterLevel)
    const xTankTopGate = tank.xLeft + _w(20)
    if (state.flowIn) {
        drawFallingWater(tank);
    }
    let pipeH1 = drawHPipe(
        _x(50),
        tank.xLeft - _w(160),
        tank.yBottom - pipeWidth - _h(5),
        state.flowIn > 0
    )
    let pipeV2 = drawVPipe(
        xTankTopGate,
        tank.yTop - _h(20),
        _h(22),
        state.flowIn > 0
    )
    let pipeV1 = drawVPipe(
        pipeH1.xRight,
        pipeV2.yTop,
        pipeH1.yTop - pipeV2.yTop,
        state.flowIn > 0
    )
    elbow(
        pipeH1.xRight,
        pipeH1.yTop,
        0,
        Math.PI / 2,
        state.flowIn
    )
    elbow(
        pipeV1.xRight,
        pipeV1.yTop,
        Math.PI,
        3 * Math.PI / 2,
        state.flowIn
    )
    let pipeH2 = drawHPipe(
        pipeV1.xRight,
        pipeV2.xLeft - pipeV1.xRight,
        pipeV2.yTop - pipeWidth,
        state.flowIn
    )
    elbow(
        pipeH2.xRight,
        pipeH2.yBottom,
        3 * Math.PI / 2,
        2 * Math.PI,
        state.flowIn
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
        state.pumpOut
    )
    let pipeOutH3 = drawHPipe(
        pipeOutH2.xRight - _w(2),
        _x(950) - pipeOutH2.xRight,
        pipeH1.yTop,
        true
    )

    drawPump(
        _x(100),
        pipeH1.yMiddle,
        state.pumpIn,
        state.isMotorInBlocked,
        state.isMotorInBlocked ? null : (state.pumpIn ? links.pumpInOff : links.pumpInOn)
    )
    drawPump(
        pipeOutH1.xRight,
        pipeOutH1.yMiddle,
        state.pumpOut,
        state.isMotorOutBlocked,
        state.isMotorOutBlocked ? null : (state.pumpOut ? links.pumpOutOff : links.pumpOutOn)
    )
    drawFilter(
        tank.xLeft - _w(280),
        pipeOutH1.yMiddle,
        state.flowIn,
        state.isFilterInBlocked
    )

    let flowmeterIn = drawFlowmeter(
        tank.xLeft - _w(240),
        yFlowmeter,
        pipeH1.yTop,
        state.flowIn
    )
    let flowmeterOut = drawFlowmeter(
        tank.xRight + _w(200),
        yFlowmeter,
        pipeOutH1.yTop,
        state.flowOut
    )
    let pipeUrbanV = drawVPipe(
        pipeOutH2.xRight - pipeWidth,
        _h(200),
        pipeOutH1.yTop - _h(198),
        !state.pumpOut
    )
    drawUrbanConnection(pipeUrbanV.xRight, pipeOutH3.yTop, state.pumpOut)
    drawLabel(_x(0), pipeH1.yMiddle, "Puits")
    drawLabel(pipeOutH3.xRight + _w(10), pipeOutH1.yMiddle, "Ferme")
    drawLabel(pipeUrbanV.xMiddle, pipeUrbanV.yTop - _h(20), "Ville", 16, true)
};
