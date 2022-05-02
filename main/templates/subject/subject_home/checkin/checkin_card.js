checkIn(){
    app.working = true;
    app.sendMessage("check_in", {"software_version" : app.software_version, "current_period" : app.session.current_period});
},

/**
 * take result of check of button press
 */
takeCheckIn(messageData){
    app.working = false;

    if(messageData.status.value == "success")
    {
        app.session_player = messageData.status.result.session_player;       
        app.session =  messageData.status.result.session;
        
        app.check_in_error_message = "";

        app.updateGraph();
    } 
    else
    {
        app.check_in_error_message =  "Error: " + messageData.status.result.error_message;
    }
},

/**
 * take result of group member pressing their check in button
 */
takeCheckInUpdate(messageData){
    app.session =  messageData.status.result.session;
    app.updateGraph();
},