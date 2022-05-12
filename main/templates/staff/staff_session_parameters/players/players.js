/**show edit parameter set player
 */
 showEditParametersetPlayer:function(index){
    
    if(app.session.started) return;
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPlayerBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_players[index]);

    app.parametersetPlayerBeforeEditIndex = index;
    app.current_parameter_set_player = app.session.parameter_set.parameter_set_players[index];

    app.editParametersetPlayerModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetPlayer:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_players[app.parametersetPlayerBeforeEditIndex], app.parametersetPlayerBeforeEdit);

        app.parametersetPlayerBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetPlayer(){

    if(app.session.started) return;
    
    app.working = true;
    app.sendMessage("update_parameterset_player", {"sessionID" : app.sessionID,
                                                   "paramterset_player_id" : app.current_parameter_set_player.id,
                                                   "formData" : $("#parametersetPlayerForm").serializeArray(),});
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

/** update parameterset player group settings
*/
sendUpdateParametersetPlayerGroup(){
    
    app.working = true;
    app.sendMessage("update_parameterset_player_group", {"sessionID" : app.sessionID,
                                                         "paramterset_player_group_id" : app.current_parameter_set_player_group.id,
                                                         "formData" : $("#parametersetPlayerGroupForm").serializeArray(),});
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
