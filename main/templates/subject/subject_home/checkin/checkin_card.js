checkIn(){
    app.working = true;
    app.sendMessage("check_in", {});
},

takeCheckIn(messageData){
    app.working = false;

    if(messageData.status.value == "success")
    {
        app.session_player.checked_in_today = messageData.status.result.check_in;        
        app.session_player.group_checked_in_today = messageData.status.result.group_checked_in_today; 
        app.session_player.earnings_individual = messageData.status.result.earnings_individual;        
        app.session_player.earnings_group = messageData.status.result.earnings_group; 
        app.session_player.earnings_total = messageData.status.result.earnings_total;
        app.check_in_error_message = "";
    } 
    else
    {
        app.check_in_error_message =  "Error: " + messageData.status.result.error_message;
    }
},