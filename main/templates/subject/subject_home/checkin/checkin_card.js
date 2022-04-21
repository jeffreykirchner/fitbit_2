checkIn(){
    app.working = true;
    app.sendMessage("check_in", {"software_version" : app.software_version});
},

takeCheckIn(messageData){
    app.working = false;

    if(messageData.status.value == "success")
    {
        app.session_player = messageData.status.result.session_player;        
        
        app.check_in_error_message = "";

        sp = app.findSessionPlayer(app.session_player.id);

        for(i=0;i<sp.session_player_periods_2.length;i++)
        {
            if(sp.session_player_periods_2[i].period_number == app.session.current_period)
            {
                sp.session_player_periods_2[i].check_in = app.session_player.checked_in_today;
                sp.session_player_periods_2[i].earnings_individual = app.session_player.earnings_individual;
                sp.session_player_periods_2[i].earnings_group = app.session_player.earnings_group;
                break;
            }
        }

        app.updateGraph();
    } 
    else
    {
        app.check_in_error_message =  "Error: " + messageData.status.result.error_message;
    }
},