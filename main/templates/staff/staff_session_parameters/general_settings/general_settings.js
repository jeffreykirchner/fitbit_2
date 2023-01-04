

/**show edit paramter set
 */
showEditParameterset:function(){
    app.clearMainFormErrors();

    app.current_parameter_set = Object.assign({}, app.session.parameter_set);

    app.editParametersetModal.toggle();
},

/** update parameterset settings
*/
sendUpdateParameterset(){
    
    app.working = true;
    app.sendMessage("update_parameterset", {"sessionID" : app.sessionID,
                                            "formData" : app.current_parameter_set,});
},

/** handle result of updating parameter set
*/
takeUpdateParameterset(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
        app.editParametersetModal.hide();            
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

