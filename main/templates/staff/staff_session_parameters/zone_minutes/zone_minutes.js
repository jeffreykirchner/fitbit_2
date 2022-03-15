

/**show edit parameter set active miutes
 */
 showEditParametersetZoneMinutes:function(index){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetZoneMinutesBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_zone_minutes[index]);
    app.parametersetZoneMinutesBeforeEditIndex = index;

    app.current_parameter_set_zone_minutes = app.$data.session.parameter_set.parameter_set_zone_minutes[index];

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetZoneMinutesModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit parameter set active minutes
*/
hideEditParametersetZoneMinutes:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_zone_minutes[app.parametersetZoneMinutesBeforeEditIndex], app.parametersetZoneMinutesBeforeEdit);
        app.parametersetZoneMinutesBeforeEdit=null;
    }
},

/** update parameterset active minutes settings
*/
sendUpdateZoneMinutes(){
    
    app.working = true;
    app.cancelModal=false;
    app.sendMessage("update_parameterset_zone_minutes", {"sessionID" : app.sessionID,
                                                           "formData" : app.current_parameter_set_zone_minutes,});
},

/** handle result of updating parameter set active minutes
*/
takeUpdateZoneMinutes(messageData){

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
        $('#editParametersetZoneMinutesModal').modal('hide');            
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/**
 * add or remove value from active minutes
 */
sendAddParameterSetZoneMinutes(value){
    app.$data.working = true;
    app.sendMessage("add_parameterset_zone_minutes", {"sessionID" : app.sessionID,
                                                        "value" : value,});
},

/**
 * take result from sendAddParameterSetZoneMinutes
 */
takeAddParameterSetZoneMinutes(messageData){
    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {     
        app.session.parameter_set = messageData.status.parameter_set;      
    } 
},

