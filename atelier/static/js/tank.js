var Tank = function(svg, state) {
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

    function _x(x) {
        return (x / _widthRef) * innerWight
    }

    function _y(y) {
        return (y / _heightRef) * innerHeight
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

    function drawTank(x, waterVolumeRatio) {
        let w = _x(150),
            y = _y(50),
            h = _y(340),
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

        return {
            xLeft: x,
            xRight: x + w,
            yTop: y,
            yBottom: y + h
        };
    }

    function drawPump(xCenter, yCenter, isOn, isBlocked) {
        let bg = "white"
        if (isBlocked) bg = "rgb(255, 105, 97)"
        else if (isOn) bg = waterColor
        let pump = rc.circle(xCenter, yCenter, pumpDiameter, {
            roughness: 0,
            strokeWidth,
            fill: bg,
            fillStyle: "solid"
        })

        svg.appendChild(pump)
        drawLabel(xCenter + _x(2), yCenter + _y(3), "P", _y(40), true);
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
        let angleDelta = 0.2
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
            tank.yTop - _y(5),
            pipeWidth,
            tank.yBottom - tank.yTop - _y(5)
        );
    }

    function drawUrbanConnection(x, y, pumpOutEnabled) {
        if (pumpOutEnabled) return
        line = rc.line(x, y, x, y + pipeWidth, { roughness: 0, strokeWidth })
        svg.appendChild(line)
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
    }
    
    const pipeWidth = _y(25)
    const yFlowmeter = _y(250)
    const wFlowmeter = _x(100)
    const hFlowmeter = _y(50)
    const pumpDiameter = _y(60)

    // TODO: read args from template
    //drawFlowmeter(xFlowmeterIn, yFlowmeterIn, 0)
    //drawPump(xTank - _x(150), false)
    let tank = drawTank(_x(450), state.waterLevel)
    const xTankTopGate = tank.xLeft + _x(20)
    if (state.flowIn) {
        drawFallingWater(tank);
    }
    //drawTankWaterBorder(tank, xTankTopGate, state.waterLevel);
    let pipeH1 = drawHPipe(
        _x(10),
        tank.xLeft - _x(50),
        tank.yBottom - pipeWidth - _y(5),
        state.flowIn > 0
    )
    let pipeV2 = drawVPipe(
        xTankTopGate,
        tank.yTop - _y(20),
        _y(22),
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
        tank.xRight - _x(3),
        _x(175),
        pipeH1.yTop,
        true
    )
    let pipeOutH2 = drawHPipe(
        pipeOutH1.xRight,
        _x(75),
        pipeH1.yTop,
        state.pumpOut
    )
    let pipeOutH3 = drawHPipe(
        pipeOutH2.xRight - _x(2),
        _x(950) - pipeOutH2.xRight,
        pipeH1.yTop,
        true
    )

    drawPump(tank.xLeft - _x(200), pipeH1.yMiddle, state.pumpIn, state.isMotorInBlocked)
    drawPump(pipeOutH1.xRight, pipeOutH1.yMiddle, state.pumpOut, state.isMotorOutBlocked)

    let flowmeterIn = drawFlowmeter(
        tank.xLeft - _x(160),
        yFlowmeter,
        pipeH1.yTop,
        state.flowIn
    )
    let flowmeterOut = drawFlowmeter(
        tank.xRight + _x(30),
        yFlowmeter,
        pipeOutH1.yTop,
        state.flowOut
    )
    let pipeUrbanV = drawVPipe(
        pipeOutH2.xRight,
        _y(200),
        pipeOutH1.yTop - _y(198),
        !state.pumpOut
    )
    let pipeUrbanH = drawHPipe(
        pipeUrbanV.xRight,
        _x(950) - pipeUrbanV.xRight,
        pipeUrbanV.yTop - pipeWidth,
        !state.pumpOut
    )
    elbow(
        pipeUrbanV.xRight,
        pipeUrbanV.yTop,
        Math.PI,
        3 * Math.PI / 2,
        !state.pumpOut
    )
    drawUrbanConnection(pipeUrbanV.xLeft, pipeOutH2.yTop, state.pumpOut)
    drawLabel(pipeOutH3.xRight + _x(10), pipeOutH1.yMiddle, "Ferme")
    drawLabel(pipeUrbanH.xRight + _x(10), pipeUrbanH.yMiddle, "Ville")
};
