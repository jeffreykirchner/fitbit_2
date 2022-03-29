/**
 * setup canvas
 */
drawSetup(chartID){
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

    let tempX = marginY;
    let tempXValue=xMin;     

    for(let i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);

        if(i%7==0)
           ctx.fillText(Math.round(tempXValue).toString(),tempX,h-marginX+18);

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

    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');           

    var w = app.sizeW;
    var h = app.sizeH;

    var marginY=app.marginY;
    var marginX=app.marginX;
    var margin2=app.margin2;

    ctx.save();

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

    let payments_list = app.session.current_parameter_set_period.parameter_set_period_payments;
    let previous_zone_minutes = 0;

    for(let i=0;i<payments_list.length;i++)
    {
        let current_zone_minutes = Math.min(payments_list[i].parameter_set_zone_minutes.zone_minutes + 1, 
                                            app.session.parameter_set.graph_y_max);
        let y = app.convertToY((current_zone_minutes+previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);

        
        ctx.fillText(payments_list[i].parameter_set_zone_minutes.label + " min.", w/2 - marginY, y+4);

        previous_zone_minutes = payments_list[i].parameter_set_zone_minutes.zone_minutes + 1;
    }

    ctx.restore();
},

/**
 * draw earnings on right side
 */
drawEarnings(chartID, yMin, yMax, xMin, xMax)
{
    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');

    let w = app.sizeW;
    let h = app.sizeH;

    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;

    let payments_list = app.session.current_parameter_set_period.parameter_set_period_payments;

    // axis
    ctx.beginPath();
    ctx.moveTo(w-marginY, h-marginX);
    ctx.lineTo(w-marginY, margin2);
    ctx.strokeStyle='Black';
    ctx.lineWidth=3;
    ctx.lineCap = "round";
    ctx.stroke();

    ctx.save()
    ctx.beginPath();
    ctx.translate(marginY, h-marginX);
    ctx.font="bold 14px Georgia";
    ctx.fillStyle = "black";
    ctx.textAlign = "left";
    ctx.lineCap = "round";

    let previous_zone_minutes = 0;

    for(let i=0;i<payments_list.length;i++)
    {
        let current_zone_minutes = Math.min(payments_list[i].parameter_set_zone_minutes.zone_minutes + 1, 
                                            app.session.parameter_set.graph_y_max);
        y = app.convertToY((current_zone_minutes+previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);

        ctx.fillText("$" + payments_list[i].payment, w-marginY-marginY+4, y+4);

        previous_zone_minutes = payments_list[i].parameter_set_zone_minutes.zone_minutes + 1;
    }

    ctx.restore();

    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 16px Georgia"; 

    ctx.save();
    ctx.translate(w-14, h/2);
    ctx.rotate(Math.PI/2);                                                              
    ctx.fillText("Your Zone Minute Earnings per Day",0,0);
    ctx.restore();
},

/**
 * draw zone minutes lines for each person in the group
 */
drawZoneMinuteLines(chartID, yMin, yMax, xMin, xMax){

    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        for(let j=0;j<player.session_player_periods.length;j++)
        {
            let session_player_period = player.session_player_periods[j];

            if(session_player_period.period_number<app.session.current_period)
            {
                dataSet.push({x:session_player_period.period_number, y:session_player_period.zone_minutes});
            }
        }

        app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                     3, app.session.session_players[i].parameter_set_player.display_color);
    }

},

/**
 * draw period earnings
 */
drawPeriodEarnings(chartID, yMin, yMax, xMin, xMax, xTickCount){

    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');

    let w = app.sizeW;
    let h = app.sizeH;

    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;

    let local_session_player = null;
   
    ctx.font="14px Georgia";
    ctx.fillStyle = app.session_player.parameter_set_player.display_color;                                                        
    ctx.textAlign = "center";

    let xScale = xMax-xMin;
    let tempX = marginY;
    let tempXValue=xMin;     
    let xTickValue=xScale/parseFloat(xTickCount);

    for(let i=0; i<=xTickCount; i++)
    {                                       
        let text = "";

        if(app.session_player.session_player_periods[i].period_number>app.session.current_parameter_set_period.period_number)
        {
            break;
        }

        if(app.session_player.session_player_periods[i].check_in)
        {
            text = '$' + app.session_player.session_player_periods[i].earnings_total;
        }
        else
        {
            text = "NP";
        }

        ctx.fillText(text, tempX, 18);

        tempX += ((w-marginY-marginY)/ (xTickCount));
        tempXValue += xTickValue;
    }


    //draw player earnings
    // for(let i=0;i<session.session_players.length;i++)
    // {
    //     if(session.session_players[i].id == )
    //     local_session_player = 
    // }
},

/**
 * re-draw graph
 */
updateGraph(){
    app.drawSetup("graph_id");

    parameter_set_period = app.session.current_parameter_set_period;

    app.drawAxis("graph_id", 
                 0, app.session.parameter_set.graph_y_max, 1,
                 parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number,
                 (parameter_set_period.graph_end_period_number-parameter_set_period.graph_start_period_number),
                 "Daily Zone Minutes", "Day");
    
    app.drawZoneMinuteAxis("graph_id", 0, app.session.parameter_set.graph_y_max,
                        parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number);

    app.drawEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                     parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number);
    
    app.drawZoneMinuteLines("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number);
    
    app.drawPeriodEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_start_period_number, parameter_set_period.graph_end_period_number,
                            (parameter_set_period.graph_end_period_number-parameter_set_period.graph_start_period_number));
},