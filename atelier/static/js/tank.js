var Tank = function(svg, state) {
    const padding = 5
    const _widthRef = 1000 + 2 * padding
    const _heightRef = 400 + 2 * padding
    // TODO
    var _width = _widthRef,
        _height = 300
    svg.setAttribute("width", _width + "px")
    svg.setAttribute("height", _height + "px")
    //svg.style.border = "1px solid #000" // TODO

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

    function heightToBottom(y) {
        return innerHeight - y
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
            h = heightToBottom(y),
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

    function drawPump(x, running) {
        // TODO: running
        // TODO: motor blocked
        // TODO: filter blocked
        let pump = rc.circle(x, heightToBottom(pumpDiameter / 2.0), pumpDiameter, {
            roughness: 0.5,
        })
        svg.appendChild(pump)
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
    
    const pipeWidth = _y(25)

    const yFlowmeter = _y(250)
    const wFlowmeter = _x(100)
    const hFlowmeter = _y(50)

    // TODO: read args from template
    //drawFlowmeter(xFlowmeterIn, yFlowmeterIn, 0)
    //drawPump(xTank - _x(150), false)
    let tank = drawTank(_x(550), state.waterLevel)
    const xTankTopGate = tank.xLeft + _x(20)
    if (state.flowIn) {
        drawFallingWater(tank);
    }
    //drawTankWaterBorder(tank, xTankTopGate, state.waterLevel);
    let pipeH1 = drawHPipe(
        _x(10),
        tank.xLeft - _x(100),
        _y(370),
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

    let pipeH3 = drawHPipe(
        tank.xRight - _x(5),
        _x(200),
        pipeH1.yTop,
        true
    )
    let flowmeterIn = drawFlowmeter(
        tank.xLeft - _x(230),
        yFlowmeter,
        pipeH1.yTop,
        state.flowIn
    )
    let flowmeterOut = drawFlowmeter(
        tank.xRight + _x(30),
        yFlowmeter,
        pipeH3.yTop,
        state.flowOut
    )
};
