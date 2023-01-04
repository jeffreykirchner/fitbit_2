/**
 * add or remove value from number of periods
 */
sendAddParameterSetPayBlock(value){
    app.working = true;
    app.sendMessage("add_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                   "value" : value,
                                                   });
},

takeAddParameterSetPayBlock(messageData){
    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {   
        app.session.parameter_set = messageData.status.parameter_set;      
    } 
},