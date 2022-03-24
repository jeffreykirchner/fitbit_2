/**
 * draw axis
 */
drawAxis(chartID, yMin, yMax, yTickCount, xMin, xMax, xTickCount, yLabel, xLabel){
    
    if(document.getElementById(chartID) == null)
    {
        return;
    }

    var canvas = document.getElementById(chartID),
        ctx = canvas.getContext('2d');     
    
    var scale = window.devicePixelRatio; // Change to 1 on retina screens to see blurry canvas.

    var card = document.getElementById("id_graph_card");

    var sizeW = card.clientWidth-40;
    var sizeH = 500;

    canvas.style.width = sizeW + "px";
    canvas.style.height = sizeH + "px";

    canvas.width = Math.floor(sizeW * scale);
    canvas.height = Math.floor(sizeH * scale);

    ctx.scale(scale, scale);

    var xScale = xMax-xMin;
    var yScale = yMax-yMin;

    var w = sizeW;
    var h = sizeH;
    var marginY=45;
    var marginX=40;
    var margin2=10;
    var tickLength=3;
    
    var xTickValue=xScale/parseFloat(xTickCount);
    var yTickValue=yScale/parseFloat(yTickCount);

    ctx.moveTo(0, 0);

    //clear screen
    // ctx.fillStyle = "white";
    // ctx.fillRect(0,0,w,h);
    ctx.clearRect(0,0,w,h);
    ctx.strokeStyle="black";
    ctx.lineWidth=3;

    //axis
    ctx.beginPath();
    ctx.moveTo(marginY, margin2);
    ctx.lineTo(marginY, h-marginX);
    ctx.lineTo(w-margin2, h-marginX);
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();

    //y ticks
    ctx.beginPath();                                                               
    ctx.font="12px Georgia";
    ctx.fillStyle = "black";
    ctx.textAlign = "right";

    var tempY = h - marginX;     
    var tempYValue = yMin;

    for(var i=0;i <= yTickCount;i++)
    {                                       
        ctx.moveTo(marginY, tempY);                                   
        ctx.lineTo(marginY-5, tempY);

        if(yMax == 1)
        {
            ctx.fillText(tempYValue.toFixed(1), marginY-8, tempY+4);
        }
        else
        {
            ctx.fillText(tempYValue, marginY-8, tempY+4);
        }

        tempY -= ((h-marginX-margin2) / (yTickCount));
        
        tempYValue += yTickValue;
    }

    ctx.stroke();

    //x ticks
    ctx.beginPath();                                                               
    ctx.textAlign = "center";

    var tempX = marginY;
    var tempXValue=xMin;     

    for(var i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);

        if(i%7==0)
           ctx.fillText(Math.round(tempXValue).toString(),tempX,h-marginX+18);

        tempX += ((w-marginY-margin2)/ (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.stroke();

    //labels
    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 14px Georgia"; 

    ctx.save();
    ctx.translate(14, h/2);
    ctx.rotate(-Math.PI/2);                                                              
    ctx.fillText(yLabel,0,0);
    ctx.restore();

    ctx.fillText(xLabel,w/2,h-4);
    ctx.restore();                       
},

/**
 * draw line on graph
 */
drawLine(chartID, yMin, yMax, xMin, xMax, dataSet, markerWidth, markerColor){


    if(document.getElementById(chartID) == null)
    {
        return;
    }

    var canvas = document.getElementById(chartID),
        ctx = canvas.getContext('2d');           

    var w =  ctx.canvas.width;
    var h = ctx.canvas.height;
    var marginY=45;
    var marginX=40;
    var margin2=10;
    var tickLength=3;

    ctx.save();

    ctx.translate(marginY, h-marginX);
    ctx.moveTo(0, 0);

    ctx.beginPath();
    for(i=0;i<dataSet.length;i++)
    {
        x = app.convertToX(dataSet[i].x,xMax,xMin,w-marginY-margin2,markerWidth);
        y = app.convertToY(dataSet[i].y,yMax,yMin,h-marginX-margin2,markerWidth);

        ctx.lineTo(x,y);
    }    

    ctx.strokeStyle=markerColor;
    ctx.lineWidth=markerWidth;
    ctx.stroke();    
    ctx.restore();                                         
},

/**
 * convert X data point to X graph point
 */
convertToX(tempValue, maxValue, minValue, tempWidth, markerWidth){
    tempT = tempWidth / (maxValue-minValue);

    tempValue-=minValue;

    if(tempValue>maxValue) tempValue=maxValue;

    return (tempT * tempValue - markerWidth/2);
},

/**
 * convert X data point to X graph point
 */
convertToY(tempValue, maxValue, minValue, tempHeight, markerHeight){
    tempT = tempHeight / (maxValue-minValue);

    if(tempValue > maxValue) tempValue=maxValue;
    if(tempValue < minValue) tempValue=minValue;

    tempValue-=minValue;

    if(tempValue>maxValue) tempValue=maxValue;

    return(-1 * tempT * tempValue - markerHeight/2)
},

/**
 * re-draw graph
 */
updateGraph(){
    parameter_set_period = app.session.current_parameter_set_period;

    app.drawAxis("graph_id", 
                 0, app.session.parameter_set.graph_y_max, 1,
                 parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number,
                 (parameter_set_period.graph_end_period_number-parameter_set_period.graph_start_period_number),
                 "Zone Minutes", "Day")
},