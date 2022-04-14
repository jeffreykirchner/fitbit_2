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
drawAxis(chartID, yMin, yMax, yTickCount, xMin, xMax, xTickCount, yLabel, xLabel, today){
    
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
    
    todayX = 0;
    todayY = 0;

    for(let i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);

        if(i%7==0 || tempXValue==today)
        {
            text = Math.round(tempXValue).toString();

            if(i==0)
            {
                text = "Day " + text;
            }
            
            //highlight today
            if(tempXValue==today)
            {
               todayX = tempX;
               todayY = h-marginX+18;
            }
            // else
            // {
            //     ctx.fillStyle = "black";
            // }
           ctx.fillText(text, tempX, h-marginX+18);
        }

        tempX += ((w-marginY-marginY)/ (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.stroke();
    ctx.closePath();

    //draw today
    ctx.beginPath();

    ctx.fillStyle = "goldenrod";
    ctx.fillText(today, todayX, todayY);
    tempW = ctx.measureText(today).width;
    tempH = 12;
    ctx.rect(todayX - tempW/2-3, todayY - tempH/2 - 6, tempW+6, tempH+6); 
    ctx.lineWidth = 1;
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
    ctx.fillText(yLabel, 0, 15);
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
drawEarnings(chartID, yMin, yMax, xMin, xMax, period_type)
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
    ctx.textAlign = "left";
    ctx.lineCap = "round";

    let previous_zone_minutes = 0;

    for(let i=0;i<payments_list.length;i++)
    {
        let current_zone_minutes = Math.min(payments_list[i].parameter_set_zone_minutes.zone_minutes + 1, 
                                            app.session.parameter_set.graph_y_max);
        y = app.convertToY((current_zone_minutes+previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);
        
        if (period_type=="Group Pay")
        {
            ctx.fillStyle = app.session_player.parameter_set_player.display_color;
            ctx.fillText("$" + payments_list[i].payment, w-marginY-marginY+4, y-10);

            ctx.fillStyle = "green";
            ctx.fillText("$" + payments_list[i].group_bonus, w-marginY-marginY+4, y+10);
        }
        else
        {
            ctx.fillStyle = app.session_player.parameter_set_player.display_color;
            ctx.fillText("$" + payments_list[i].payment, w-marginY-marginY+4, y+4);
        }

        previous_zone_minutes = payments_list[i].parameter_set_zone_minutes.zone_minutes + 1;
    }

    ctx.restore();

    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 16px Georgia"; 

    ctx.save();
    ctx.translate(w-14, (h-marginX-margin2)/2+margin2);
    ctx.rotate(Math.PI/2);                                                              
    ctx.fillText("Your Potential Zone Minute Earnings per Day", 0, 10);
    ctx.restore();
},

/**
 * draw zone minutes lines for each person in the group
 */
 drawZoneMinuteLines1(chartID, yMin, yMax, xMin, xMax){

    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        for(let j=0;j<player.session_player_periods_1.length;j++)
        {
            let session_player_period = player.session_player_periods_1[j];

            if(session_player_period.period_number<app.session.current_period)
            {
                dataSet.push({x:session_player_period.period_number, y:session_player_period.zone_minutes});
            }
        }

        app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                     3, app.session.session_players[i].parameter_set_player.display_color, 0.25,[3, 10]);
    }

},

/**
 * draw zone minutes lines for each person in the group
 */
drawZoneMinuteLines2(chartID, yMin, yMax, xMin, xMax){

    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        for(let j=0;j<player.session_player_periods_2.length;j++)
        {
            let session_player_period = player.session_player_periods_2[j];

            if(session_player_period.period_number<app.session.current_period)
            {
                dataSet.push({x:session_player_period.period_number, y:session_player_period.zone_minutes});
            }
        }

        app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                     3, app.session.session_players[i].parameter_set_player.display_color, 1,[1]);
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
                                                           
    ctx.textAlign = "center";

    let xScale = xMax-xMin;
    let tempX = marginY;
    let tempXValue=xMin;     
    let xTickValue=xScale/parseFloat(xTickCount);

    let session_player_partner = null;

    for(let i=0;i<app.session.session_players.length;i++)
    {
        if(app.session.session_players[i].id != app.session_player.id)
        {
            session_player_partner = app.session.session_players[i]
            break;
        }
    }

    for(let i=0; i<=xTickCount; i++)
    {                                       
        let text1 = "";
        let text2 = "";

        if(i==0)
        {
            ctx.textAlign = "left";
        }
        else if(i==xTickCount)
        {
            ctx.textAlign = "right";
        }
        else
        {
            ctx.textAlign = "center";
        }
        
        let show_team_pay_label = false;

        if(app.session_player.session_player_periods_2[i].period_number>app.session.current_parameter_set_period.period_number)
        {
            break;
        }

        //mute payments outside of current payblock
        if(app.session_player.session_player_periods_2[i].pay_block == app.session.current_parameter_set_period.pay_block)
        {
            ctx.globalAlpha = 1;
        }
        else
        {
            ctx.globalAlpha = 0.5;
        }

        //local player
        ctx.fillStyle = app.session_player.parameter_set_player.display_color;

        if(app.session_player.session_player_periods_2[i].check_in)
        {
            text1 = '$' + app.session_player.session_player_periods_2[i].earnings_individual;
            text2 = '$' + app.session_player.session_player_periods_2[i].earnings_group;
        }
        else
        {
            text1 = "NP";
            text2 = "NP";
        }

        ctx.fillText(text1, tempX, h-marginX+40);

        if(app.session_player.session_player_periods_2[i].period_type == "Group Pay")
        {
            ctx.fillStyle = "green";
            ctx.fillText(text2, tempX, h-marginX+64);
            show_team_pay_label = true;
        }

        //partner
        ctx.fillStyle = session_player_partner.parameter_set_player.display_color;
        if(session_player_partner.session_player_periods_2[i].check_in)
        {
            text1 = '$' + session_player_partner.session_player_periods_2[i].earnings_individual;
        }
        else
        {
            text1 = "NP";
        }

        ctx.fillText(text1, tempX, 18);

        tempX += ((w-marginY-marginY) / (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.globalAlpha = 1;
    //labels
    ctx.fillStyle = session_player_partner.parameter_set_player.display_color;
    ctx.textAlign = "right";
    ctx.fillText("Partner", marginY-25, 15);
    ctx.fillText("Pay", marginY-30, 28);

    ctx.fillStyle = app.session_player.parameter_set_player.display_color;
    ctx.fillText("My Pay", marginY-25, h-marginX+40);

    ctx.fillStyle = "green";
    ctx.fillText("Group", marginY-25, h-marginX+57);
    ctx.fillText("Pay", marginY-30, h-marginX+70);

    //totals
    ctx.fillStyle = session_player_partner.parameter_set_player.display_color;
    ctx.textAlign = "right";
    ctx.fillText("Sum=$"+session_player_partner.current_block_earnings.individual, w - 5, 18);

    ctx.fillStyle = app.session_player.parameter_set_player.display_color;
    ctx.textAlign = "right";
    ctx.fillText("Sum=$"+app.session_player.current_block_earnings.individual, w - 5, h-marginX+40);

    ctx.fillStyle = "green";
    ctx.textAlign = "right";
    ctx.fillText("Sum=$"+app.session_player.current_block_earnings.group_bonus, w - 5, h-marginX+64);
},

/**
 * re-draw graph
 */
updateGraph(){
    if(app.session.finished || app.session.is_after_last_period || app.session.is_before_first_period) return;

    app.drawSetup("graph_id");

    parameter_set_period = app.session.current_parameter_set_period;

    app.drawAxis("graph_id", 
                 0, app.session.parameter_set.graph_y_max, 1,
                 parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number,
                 (parameter_set_period.graph_2_end_period_number-parameter_set_period.graph_2_start_period_number),
                 "Daily Zone Minutes", "Day", parameter_set_period.period_number);
    
    app.drawZoneMinuteAxis("graph_id", 0, app.session.parameter_set.graph_y_max,
                           parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);

    app.drawEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                     parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number,
                     parameter_set_period.period_type);
    
    if(parameter_set_period.show_graph_1)
        app.drawZoneMinuteLines1("graph_id", 0, app.session.parameter_set.graph_y_max,
                                 parameter_set_period.graph_1_start_period_number, parameter_set_period.graph_1_end_period_number);

    app.drawZoneMinuteLines2("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);
    

    app.drawPeriodEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number,
                            (parameter_set_period.graph_2_end_period_number-parameter_set_period.graph_2_start_period_number));
    
},