/**
 * setup canvas
 */
drawSetup(chartID){

    if(!app.session) return;

    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');     

    let scale = window.devicePixelRatio;

    let card = document.getElementById("id_graph_card");

    app.sizeW = card.clientWidth-40;
    app.sizeH = 500;

    canvas.style.width = app.sizeW + "px";
    canvas.style.height = app.sizeH + "px";

    canvas.width = Math.floor(app.sizeW * scale);
    canvas.height = Math.floor(app.sizeH * scale);

    ctx.scale(scale, scale);
},

/**
 * convert X data point to X graph point
 */
 convertToX(tempValue, maxValue, minValue, tempWidth, markerWidth){
    tempT = parseFloat(tempWidth) / parseFloat(maxValue-minValue);

    tempValue = parseFloat(tempValue) - parseFloat(minValue);

    if(tempValue>maxValue) tempValue=parseFloat(maxValue);

    return (tempT * tempValue);
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
 * draw axis
 */
drawAxis(chartID, yMin, yMax, yTickCount, xMin, xMax, xTickCount, yLabel, xLabel){
    
    if(document.getElementById(chartID) == null)
    {
        return;
    }

    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');  

    let xScale = parseFloat(xMax-xMin);
    let yScale = parseFloat(yMax-yMin);

    let w = app.sizeW;
    let h =  app.sizeH;

    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;
    let tickLength=3;
    
    let xTickValue=xScale/parseFloat(xTickCount);
    let yTickValue=yScale/parseFloat(yTickCount);

    ctx.save();

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
    ctx.lineTo(w-marginY, h-marginX);
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();

    //y ticks
    ctx.beginPath();                                                               
    ctx.font="bold 16px Georgia";
    ctx.fillStyle = "black";
    ctx.textAlign = "right";

    let tempY = h - marginX;     
    let tempYValue = yMin;

    for(let i=0;i <= yTickCount;i++)
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
    ctx.font="bold 14px Georgia";

    let tempX = marginY;
    let tempXValue=xMin;    

    for(let i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);

       
        // {
        text = Math.round(tempXValue).toString();
        //text = app.session_player.session_player_periods_2[i].period_day_of_week;

       
        // else
        // {
        //     ctx.fillStyle = "black";
        // }
        ctx.fillText(text, tempX, h-marginX+18);
        //}

        tempX += ((w-marginY-marginY)/ (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.stroke();
    ctx.closePath();
    

    //labels
    ctx.restore();
    ctx.save()
    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 16px Georgia"; 

    ctx.save();
    ctx.translate(14, h/2);
    ctx.rotate(-Math.PI/2);                                                              
    ctx.fillText(yLabel, 0, 5);
    ctx.restore();

    // ctx.textAlign = "right";
    // ctx.fillStyle = "black";
    // ctx.fillText(xLabel, marginY-5, h-marginX+5);
    ctx.restore();                       
},

/**
 * draw line on graph
 */
drawLine(chartID, yMin, yMax, xMin, xMax, dataSet, markerWidth, markerColor, alpha, lineDash){


    if(document.getElementById(chartID) == null)
    {
        return;
    }

    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');           

    var w = app.sizeW;
    var h = app.sizeH;

    var marginY=app.marginY;
    var marginX=app.marginX;
    var margin2=app.margin2;

    ctx.save();

    ctx.setLineDash(lineDash); //[15, 3, 3, 3]
    ctx.globalAlpha = alpha;
    ctx.translate(marginY, h-marginX);
    ctx.moveTo(0, 0);

    ctx.beginPath();
    for(i=0;i<dataSet.length;i++)
    {
        x = app.convertToX(dataSet[i].x,xMax,xMin,w-marginY-marginY,markerWidth);
        y = app.convertToY(dataSet[i].y,yMax,yMin,h-marginX-margin2,markerWidth);

        ctx.lineTo(x,y);
    }    

    ctx.strokeStyle=markerColor;
    ctx.lineWidth=markerWidth;
    ctx.lineCap = "round";

    ctx.stroke();    
    ctx.restore();                                         
},

/**
 * draw right side Y axis
 */
 drawZoneMinuteAxis(chartID, yMin, yMax, xMin, xMax)
 {
     let canvas = document.getElementById(chartID);
     let ctx = canvas.getContext('2d');
 
     let w = app.sizeW;
     let h = app.sizeH;
 
     let marginY=app.marginY;
     let marginX=app.marginX;
     let margin2=app.margin2;
 
     let zone_minutes_list = app.session.parameter_set.parameter_set_zone_minutes;
 
     ctx.save();
 
     ctx.strokeStyle='LightGray';
     ctx.setLineDash([15, 3, 3, 3]);
     ctx.lineWidth=3;
 
     ctx.translate(marginY, h-marginX);
     ctx.moveTo(0, 0);
 
     //lines
     ctx.beginPath();
 
     for(let i=0;i<zone_minutes_list.length-1;i++)
     {
         y = app.convertToY(zone_minutes_list[i].zone_minutes+1, yMax, yMin, h-marginX-margin2, ctx.lineWidth);
 
         ctx.moveTo(0, y);
         ctx.lineTo(w-marginY-marginY, y);
     }
 
     ctx.stroke();
     ctx.closePath();
     ctx.restore(); 
 
     // axis
     ctx.save();
     ctx.translate(marginY, h-marginX);
     ctx.beginPath();
     ctx.strokeStyle='Black';
     ctx.lineWidth=3;
     ctx.font="bold 14px Georgia";
     ctx.fillStyle = "black";
     ctx.textAlign = "right";
     ctx.lineCap = "round";
     
     for(let i=0;i<zone_minutes_list.length-1;i++)
     {
         y = app.convertToY(zone_minutes_list[i].zone_minutes+1, yMax, yMin, h-marginX-margin2, ctx.lineWidth);
 
         ctx.fillText(zone_minutes_list[i].zone_minutes+1, -8, y+4);
         ctx.moveTo(-4, y);
         ctx.lineTo(0, y);
     }
 
     ctx.stroke();
     ctx.closePath();
 
     ctx.restore(); 
 
     //labels
     ctx.save()
 
     ctx.translate(marginY, h-marginX);
     ctx.font="bold 14px Georgia";
     ctx.fillStyle = "DimGray";
     ctx.textAlign = "center";
     ctx.lineCap = "round";
     ctx.globalAlpha = 0.25; 
    
     if(!app.session.current_parameter_set_period) return;

    let payments_list = app.session.current_parameter_set_period.parameter_set_period_payments;
    let previous_zone_minutes = 0;
 
    if (payments_list)
    {
        for(let i=0;i<payments_list.length;i++)
        {
            let current_zone_minutes = Math.min(payments_list[i].parameter_set_zone_minutes.zone_minutes + 1, 
                                                app.session.parameter_set.graph_y_max);
            let y = app.convertToY((current_zone_minutes+previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);
    
            
            ctx.fillText(payments_list[i].parameter_set_zone_minutes.label + " min.", w/2 - marginY, y+4);
    
            previous_zone_minutes = payments_list[i].parameter_set_zone_minutes.zone_minutes + 1;
        }
    }
 
     ctx.restore();
 },

 /**
  * draw median zone minutes
  */
 drawMedianZoneMinutes(chartID, yMin, yMax, xMin, xMax)
 {
    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');
 
    let w = app.sizeW;
    let h = app.sizeH;
 
    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;

    let markerWidth = 1;

    let zone_minutes_list = app.session.median_zone_minutes;
    let current_period = app.session.current_period;

    // line
    ctx.save();

    ctx.lineCap = "round";
    ctx.translate(marginY, h-marginX);
    ctx.moveTo(0, 0);
    ctx.lineWidth=markerWidth;

    ctx.beginPath();
    for(let i=0;i<current_period;i++)
    {
        x = app.convertToX(i+1, xMax, xMin, w-marginY-marginY, markerWidth);
        y = app.convertToY(zone_minutes_list[i], yMax, yMin, h-marginX-margin2, markerWidth);

        ctx.lineTo(x,y);
    }
    ctx.strokeStyle="black";
    ctx.stroke();

    //dots
    for(let i=0;i<current_period;i++)
    {
        ctx.beginPath();
        x = app.convertToX(i+1, xMax, xMin, w-marginY-marginY, markerWidth);
        y = app.convertToY(zone_minutes_list[i], yMax, yMin, h-marginX-margin2, markerWidth);
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle="gray";
        ctx.fill();
        ctx.stroke();
    }

    ctx.restore();
 },

/**
 * re-draw graph
 */
updateGraph(){

    if(!app.session) return;

    app.drawSetup("graph_id");

    parameter_set_period = app.session.current_parameter_set_period;

    app.drawAxis("graph_id", 
                 0, app.session.parameter_set.graph_y_max, 1,
                 1, app.session.parameter_set.parameter_set_periods.length, app.session.parameter_set.parameter_set_periods.length/7,
                 "Median Zone Minutes", "Day");

    app.drawZoneMinuteAxis("graph_id", 0, app.session.parameter_set.graph_y_max,
                           1,  app.session.parameter_set.parameter_set_periods.length);
    
    app.drawMedianZoneMinutes("graph_id", 0, app.session.parameter_set.graph_y_max,
                           1,  app.session.parameter_set.parameter_set_periods.length);
},