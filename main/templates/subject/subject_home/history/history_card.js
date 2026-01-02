show_person_column : function show_person_column()
{
    for(let p in app.session_player.earnings_history)
    {
        let session_players = app.session_player.earnings_history[p].session_players;
        if(session_players.length > 1)
        {
            return true;
        }
    }

    return false;
},

show_daily_pay_column : function show_daily_pay_column()
{
    for(let p in app.session_player.earnings_history)
    {
        if(app.session_player.earnings_history[p].pay_block_fixed_pay > 0)
        {
            return true;
        }
    }

    return false;
},

show_individual_pay_column : function show_individual_pay_column()
{
    for(let p in app.session_player.earnings_history)
    {
        if(app.session_player.earnings_history[p].pay_block_type == "Block Pay Group" ||
           app.session_player.earnings_history[p].pay_block_type == "Block Pay Individual" ||
           app.session_player.earnings_history[p].pay_block_type == "Block Pay Competition")
        {
            return true;
        }
    }

    return false;
},

show_bonus_pay_column : function show_bonus_pay_column()
{
    for(let p in app.session_player.earnings_history)
    {
        if(app.session_player.earnings_history[p].pay_block_type == "Block Pay Group" ||
           app.session_player.earnings_history[p].pay_block_type == "Block Pay Competition")
        {
            return true;
        }
    }

    return false;
},

show_fitbit_percent_column : function show_fitbit_percent_column()
{
    for(let p in app.session_player.earnings_history)
    {
        if(app.session_player.earnings_history[p].pay_block_type == "Earn Fitbit")
        {
            return true;
        }
    }

    return false;
},