/**show edit parameter set player
 */
 showEditParametersetPlayer:function(index){
    
    if(app.session.started) return;
    
    app.clearMainFormErrors();

    app.current_parameter_set_player =  Object.assign({}, app.session.parameter_set.parameter_set_players[index]);
    app.editParametersetPlayerModal.toggle();
},


/** update parameterset type settings
*/
sendUpdateParametersetPlayer(){

    if(app.session.started) return;

    app.working = true;
    app.sendMessage("update_parameterset_player", {"sessionID" : app.sessionID,                                                  
                                                   "formData" : app.current_parameter_set_player,});
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetPlayer(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
        app.editParametersetPlayerModal.hide();       
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** copy specified period's groups forward to future groups
*/
sendRemoveParameterSetPlayer(){
    app.working = true;
    app.sendMessage("remove_parameterset_player", {"sessionID" : app.sessionID,
                                                   "increment_player" : app.increment_player});                                               
},

/** handle result of copying groups forward
*/
takeRemoveParameterSetPlayer(messageData){

    app.session.parameter_set = messageData.status.parameter_set;   
    app.editParametersetPlayerModal.hide();
},

/** add player to parameter set
*/
sendAddParameterSetPlayer(player_id){
    app.working = true;
    app.sendMessage("add_parameterset_player", {"sessionID" : app.sessionID,
                                                "increment_player" : app.increment_player});                                                 
},

/**take result of add player
*/
takeAddParameterSetPlayer(messageData){

    app.session.parameter_set = messageData.status.parameter_set;
},
