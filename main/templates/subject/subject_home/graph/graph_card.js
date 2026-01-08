/**
 * setup canvas
 */
drawSetup: function drawSetup(chartID){

    if(!app.session) return;
    if(!app.session_player) return;

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
drawAxis: function drawAxis(chartID, yMin, yMax, yTickCount, xMin, xMax, xTickCount, yLabel, xLabel, today){
    
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
    
    todayX = 0;
    todayY = 0;
    todayText = "";

    for(let i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);

       
        // {
        //text = Math.round(tempXValue).toString();
        text = app.session_player.session_player_periods_2[i].period_day_of_week;

        if(tempXValue==today)
        {
            todayText = text;
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
        //}

        tempX += ((w-marginY-marginY)/ (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.stroke();
    ctx.closePath();

    //draw today
    ctx.beginPath();

    ctx.fillStyle = "gold";
    ctx.fillText(todayText, todayX, todayY);
    tempW = ctx.measureText(todayText).width;
    tempH = 12;
    //ctx.rect(todayX - tempW/2-3, todayY - tempH/2 - 6, tempW+6, tempH+2); 
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
drawLine: function drawLine(chartID, yMin, yMax, xMin, xMax, dataSet, markerWidth, markerColor, alpha, lineDash){


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

        if(i>0 && dataSet[i].pay_block_number != dataSet[i-1].pay_block_number)
        {
            ctx.moveTo(x,y);
        }
        else
        {
            ctx.lineTo(x,y);
        }
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
convertToX: function convertToX(tempValue, maxValue, minValue, tempWidth, markerWidth){
    tempT = parseFloat(tempWidth) / parseFloat(maxValue-minValue);

    tempValue = parseFloat(tempValue) - parseFloat(minValue);

    if(tempValue>maxValue) tempValue=parseFloat(maxValue);

    return (tempT * tempValue);
},

/**
 * convert X data point to X graph point
 */
convertToY: function convertToY(tempValue, maxValue, minValue, tempHeight, markerHeight){
    tempT = tempHeight / (maxValue-minValue);

    if(tempValue > maxValue) tempValue=maxValue;
    if(tempValue < minValue) tempValue=minValue;

    tempValue-=minValue;

    if(tempValue>maxValue) tempValue=maxValue;

    return(-1 * tempT * tempValue - markerHeight/2)
},

/**
 * draw left side Y axis
 */
drawZoneMinuteAxis: function drawZoneMinuteAxis(chartID, yMin, yMax, xMin, xMax)
{
    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');

    let w = app.sizeW;
    let h = app.sizeH;

    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;

    //let zone_minutes_list = app.session.parameter_set.parameter_set_zone_minutes;

    ctx.save();

    ctx.strokeStyle='LightGray';
    ctx.setLineDash([15, 3, 3, 3]);
    ctx.lineWidth=3;

    ctx.translate(marginY, h-marginX);
    ctx.moveTo(0, 0);

    let current_pay_block_id = app.session.current_parameter_set_period.parameter_set_pay_block.id;
    let current_pay_block = app.session.parameter_set.parameter_set_pay_blocks[current_pay_block_id];

    //lines
    ctx.beginPath();

    for(let i=0;i<current_pay_block.parameter_set_pay_block_payments_order.length-1;i++)
    {
        let index = current_pay_block.parameter_set_pay_block_payments_order[i];
        let zone_minutes = current_pay_block.parameter_set_pay_block_payments[index].zone_minutes; //zone_minutes_list[i].zone_minutes+1
        
        y = app.convertToY(zone_minutes+1, yMax, yMin, h-marginX-margin2, ctx.lineWidth);

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
    
    for(let i=0;i<current_pay_block.parameter_set_pay_block_payments_order.length-1;i++)
    {
        let index = current_pay_block.parameter_set_pay_block_payments_order[i];
        let zone_minutes = current_pay_block.parameter_set_pay_block_payments[index].zone_minutes; //zone_minutes_list[i].zone_minutes+1
        
        y = app.convertToY(zone_minutes+1, yMax, yMin, h-marginX-margin2, ctx.lineWidth);

        ctx.fillText(zone_minutes+1, -8, y+4);
        ctx.moveTo(-4, y);
        ctx.lineTo(0, y);
    }

    ctx.stroke();
    ctx.closePath();

    ctx.restore(); 

    //labels between lines
    ctx.save()

    ctx.translate(marginY, h-marginX);
    ctx.font="bold 14px Georgia";
    ctx.fillStyle = "DimGray";
    ctx.textAlign = "center";
    ctx.lineCap = "round";
    ctx.globalAlpha = 0.25;

    if(!app.session.current_parameter_set_period) return;

    let previous_zone_minutes = 0;

    for(let i=0;i<current_pay_block.parameter_set_pay_block_payments_order.length;i++)
    {
        let index = current_pay_block.parameter_set_pay_block_payments_order[i];
        let zone_minutes = current_pay_block.parameter_set_pay_block_payments[index].zone_minutes; //zone_minutes_list[i].zone_minutes+1
        let label = current_pay_block.parameter_set_pay_block_payments[index].label;

        let current_zone_minutes = Math.min(zone_minutes + 1, 
                                            app.session.parameter_set.graph_y_max);

        let y = app.convertToY((current_zone_minutes + previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);

        
        ctx.fillText(label, w/2 - marginY, y+4);

        previous_zone_minutes = zone_minutes + 1;
    }
    
    ctx.restore();
},

/**
 * draw earnings on right side
 */
drawEarnings: function drawEarnings(chartID, yMin, yMax, xMin, xMax)
{
    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');

    let w = app.sizeW;
    let h = app.sizeH;

    let marginY=app.marginY;
    let marginX=app.marginX;
    let margin2=app.margin2;

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

    let current_pay_block_id = app.session.current_parameter_set_period.parameter_set_pay_block.id;
    let current_pay_block = app.session.parameter_set.parameter_set_pay_blocks[current_pay_block_id];
    let previous_zone_minutes = 0;

    for(let i=0;i<current_pay_block.parameter_set_pay_block_payments_order.length;i++)
    {
        let index = current_pay_block.parameter_set_pay_block_payments_order[i];
        let pay_block_payment = current_pay_block.parameter_set_pay_block_payments[index];

        let current_zone_minutes = Math.min(pay_block_payment.zone_minutes + 1, app.session.parameter_set.graph_y_max);
                                            
        y = app.convertToY((current_zone_minutes + previous_zone_minutes)/2, yMax, yMin, h-marginX-margin2, ctx.lineWidth);
        
        if (current_pay_block.pay_block_type=="Block Pay Group" ||
            current_pay_block.pay_block_type=="Block Pay Competition")
        {
            ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(app.session_player.id));
            ctx.fillText("$" + pay_block_payment.payment, w-marginY-marginY+4, y-10);

            ctx.fillStyle = "green";
            ctx.fillText("$" + pay_block_payment.group_bonus, w-marginY-marginY+4, y+10);
        }
        else
        {
            ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(app.session_player.id));
            ctx.fillText("$" + pay_block_payment.payment, w-marginY-marginY+4, y+4);
        }

        previous_zone_minutes = pay_block_payment.zone_minutes + 1;
    }

    ctx.restore();

    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 16px Georgia"; 

    ctx.save();
    ctx.translate(w-5, (h-marginX-margin2)/2+margin2);
    ctx.rotate(Math.PI/2);                                                              
    ctx.fillText("Your " + app.session.current_block_length +  " Day Average Zone Minute Bonus", 0, 10);
    ctx.restore();
},

/**
 * draw zone minutes lines for each person in the group
 */
 drawZoneMinuteLines1: function drawZoneMinuteLines1(chartID, yMin, yMax, xMin, xMax){

    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        for(let j=0;j<player.session_player_periods_1.length;j++)
        {
            let session_player_period = player.session_player_periods_1[j];

            if(session_player_period.period_number<app.session.current_period)
            {
                dataSet.push({x:session_player_period.period_number, 
                              y:session_player_period.average_pay_block_zone_minutes,
                              pay_block_number: session_player_period.pay_block_number});
            }
        }

        app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                     3, app.getColor(app.findSessionPlayerIndex(app.session.session_players[i].id)), 0.25,[3, 10]);
    }

},

/**
 * draw zone minutes lines for each person in the group
 */
drawZoneMinuteLines2: function drawZoneMinuteLines2(chartID, yMin, yMax, xMin, xMax){

    //draw group
    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        
        if(player.id != app.session_player.id)
        {
            for(let j=0;j<player.session_player_periods_2.length;j++)
            {
                let session_player_period = player.session_player_periods_2[j];
                
                if(session_player_period.period_number<app.session.current_period || 
                   (session_player_period.period_number==app.session.current_period && session_player_period.check_in))
                    {
                        dataSet.push({x:session_player_period.period_number, 
                                      y:session_player_period.average_pay_block_zone_minutes,
                                      pay_block_number: session_player_period.pay_block_number});
                    }
                
            }

            app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                        3, app.getColor(app.findSessionPlayerIndex(app.session.session_players[i].id)), 1,[1]);
        }
    }

    //draw local player
    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];
        let dataSet=[];

        
        if(player.id == app.session_player.id)
        {
            for(let j=0;j<player.session_player_periods_2.length;j++)
            {
                let session_player_period = player.session_player_periods_2[j];

                if(session_player_period.period_number<app.session.current_period || 
                  (session_player_period.period_number==app.session.current_period && session_player_period.check_in))
                    {
                        dataSet.push({x:session_player_period.period_number, 
                                      y:session_player_period.average_pay_block_zone_minutes,
                                      pay_block_number: session_player_period.pay_block_number});
                    }
                
            }
            
            app.drawLine(chartID, yMin, yMax, xMin, xMax, dataSet,
                        3, app.getColor(app.findSessionPlayerIndex(app.session.session_players[i].id)), 1,[1]);


            break;
        }
    }

},

/**
 * draw dot for todays zone minutes
 */
drawZoneMinutes: function drawZoneMinutes(chartID, yMin, yMax, xMin, xMax){
    var canvas = document.getElementById(chartID);
    var ctx = canvas.getContext('2d');           

    var w = app.sizeW;
    var h = app.sizeH;

    var marginY=app.marginY;
    var marginX=app.marginX;
    var margin2=app.margin2;

    var markerWidth = 1;

    ctx.save()
    
    ctx.translate(marginY, h-marginX);
    ctx.moveTo(0, 0);
    ctx.lineWidth=markerWidth;

    //draw group
    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];

        if(player.id != app.session_player.id)
        {

            for(let j=0;j<player.session_player_periods_2.length;j++)
            {
                let session_player_period = player.session_player_periods_2[j];

                if(session_player_period.check_in)
                {
                    
                    ctx.beginPath();
                    x = app.convertToX(session_player_period.period_number, xMax, xMin, w-marginY-marginY, markerWidth);
                    y = app.convertToY(session_player_period.zone_minutes, yMax, yMin, h-marginX-margin2, markerWidth);
                    ctx.arc(x, y, 6, 0, 2 * Math.PI);
                    ctx.fillStyle=app.getColor(app.findSessionPlayerIndex(player.id));
                    ctx.fill();
                    ctx.stroke();
                }
                
            }            
        }
    }

    //draw local player
    for(let i=0;i<app.session.session_players.length;i++)
    {
        let player = app.session.session_players[i];

        if(player.id == app.session_player.id)
        {

            for(let j=0;j<player.session_player_periods_2.length;j++)
            {
                let session_player_period = player.session_player_periods_2[j];

                if(session_player_period.check_in)
                {
                    ctx.beginPath();
                    x = app.convertToX(session_player_period.period_number, xMax, xMin, w-marginY-marginY, markerWidth);
                    y = app.convertToY(session_player_period.zone_minutes, yMax, yMin, h-marginX-margin2, markerWidth);
                    ctx.arc(x, y, 6, 0, 2 * Math.PI);
                    ctx.fillStyle=app.getColor(app.findSessionPlayerIndex(player.id));
                    ctx.fill();
                    ctx.stroke();
                }
                
            }            
        }
    }

    ctx.restore();

},

/**
 * draw period earnings
 */
drawPeriodEarnings: function drawPeriodEarnings(chartID, yMin, yMax, xMin, xMax, xTickCount){

    if(app.session_player.earnings_fixed==0 && app.session_player.no_pay_percent==0) return;

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

    let current_pay_block_id = app.session.current_parameter_set_period.parameter_set_pay_block.id;
    let current_pay_block = app.session.parameter_set.parameter_set_pay_blocks[current_pay_block_id];
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
        ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(app.session_player.id));

        if(app.session_player.session_player_periods_2[i].check_in)
        {   
            if(app.session_player.session_player_periods_2[i].period_type == "Earn Fitbit")
            {
                text1 = app.session_player.session_player_periods_2[i].earnings_no_pay_percent + '%';
            }
            else
            {
                text1 = '$' + app.session_player.session_player_periods_2[i].earnings_fixed;
            }
        }
        else
        {
            text1 = "";
        }

        ctx.fillText(text1, tempX, h-marginX+40);

        
        //partner
        if(session_player_partner)
        {
            ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(session_player_partner.id));
            if(session_player_partner.session_player_periods_2[i].check_in)
            {
                if(app.session_player.session_player_periods_2[i].period_type == "Earn Fitbit")
                {
                    text1 = session_player_partner.session_player_periods_2[i].earnings_no_pay_percent + '%';
                }
                else
                {
                    text1 = '$' + session_player_partner.session_player_periods_2[i].earnings_fixed; 
                }
            }
            else
            {
                text1 = "";
            }

            ctx.fillText(text1, tempX, 18);
        }

        tempX += ((w-marginY-marginY) / (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.globalAlpha = 1;
    //labels
    if(session_player_partner)
    {
        ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(session_player_partner.id));
        ctx.textAlign = "center";
        // ctx.fillText(app.getColorName(app.findSessionPlayerIndex(session_player_partner.id))+"'s", marginY-20, 15);
        ctx.fillText(app.get_partner_string("upper"), marginY/2, 15);

        if(current_pay_block.pay_block_type == "Earn Fitbit")
        {
            ctx.fillText("Fitbit", marginY/2, 28);
        }
        else
        {
            ctx.fillText("Pay", marginY/2, 28);
        }
    }

    ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(app.session_player.id));
    ctx.textAlign = "right";
    
    if(current_pay_block.pay_block_type == "Earn Fitbit")
    {
       ctx.fillText("My Fitbit", marginY-15, h-marginX+40);
    }
    else
    {
        ctx.fillText("My Pay", marginY-25, h-marginX+40);
    }

    //totals
    //partner
    if(session_player_partner)
    {
        ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(session_player_partner.id));
        ctx.textAlign = "right";

        if(current_pay_block.pay_block_type == "Earn Fitbit")
        {
            ctx.fillText("Sum="+Math.min(session_player_partner.current_block_earnings.earnings_no_pay_percent, 100)+"%", w - 5, 18);
        }
        else
        {
            ctx.fillText("Sum=$"+session_player_partner.current_block_earnings.fixed, w - 5, 18);
        }
    }
    
    //player
    ctx.fillStyle = app.getColor(app.findSessionPlayerIndex(app.session_player.id));
    ctx.textAlign = "right";
    if(current_pay_block.pay_block_type == "Earn Fitbit")
    {
        ctx.fillText("Sum="+Math.min(app.session_player.current_block_earnings.earnings_no_pay_percent, 100)+'%', w - 5, h-marginX+40);
    }
    else
    {
        ctx.fillText("Sum=$"+app.session_player.current_block_earnings.fixed, w - 5, h-marginX+40);
    }
},

drawLoadingScreen: function drawLoadingScreen(chartID){
    let canvas = document.getElementById(chartID);
    let ctx = canvas.getContext('2d');

    let w = canvas.width;
    let h = canvas.height;

    ctx.font="14px Georgia";                              
    ctx.textAlign = "center";
    ctx.fillText("Loading ...", w/2, h/2);
},

/**
 * re-draw graph
 */
updateGraph: function updateGraph(){

    if(!app.session) return;
    if(!app.session_player) return;

    //show loading screen
    if(!app.first_load_done)
    {
        app.drawLoadingScreen("graph_id");
        return;
    }

    if(app.session.finished || app.session.is_after_last_period || app.session.is_before_first_period) return;

    app.drawSetup("graph_id");

    let parameter_set_period = app.session.current_parameter_set_period;
    let current_pay_block_id = app.session.current_parameter_set_period.parameter_set_pay_block.id;
    let current_pay_block = app.session.parameter_set.parameter_set_pay_blocks[current_pay_block_id];

    app.drawAxis("graph_id", 
                 0, app.session.parameter_set.graph_y_max, 1,
                 parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number,
                 (parameter_set_period.graph_2_end_period_number-parameter_set_period.graph_2_start_period_number),
                 "Daily Zone Minutes", "", parameter_set_period.period_number);
    
    app.drawZoneMinuteAxis("graph_id", 0, app.session.parameter_set.graph_y_max,
                           parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);

    if(current_pay_block.pay_block_type == "Block Pay Group" || 
       current_pay_block.pay_block_type == "Block Pay Individual" ||
       current_pay_block.pay_block_type == "Block Pay Competition")
    {
        app.drawEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                        parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);
    }
    
    if(parameter_set_period.show_graph_1)
        app.drawZoneMinuteLines1("graph_id", 0, app.session.parameter_set.graph_y_max,
                                 parameter_set_period.graph_1_start_period_number, parameter_set_period.graph_1_end_period_number);

    app.drawZoneMinuteLines2("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);
    
    app.drawZoneMinutes("graph_id", 0, app.session.parameter_set.graph_y_max,
                              parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number);

    app.drawPeriodEarnings("graph_id", 0, app.session.parameter_set.graph_y_max,
                            parameter_set_period.graph_2_start_period_number, parameter_set_period.graph_2_end_period_number,
                            (parameter_set_period.graph_2_end_period_number-parameter_set_period.graph_2_start_period_number));
    
},