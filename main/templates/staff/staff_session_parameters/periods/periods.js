

/**show edit parameter set periods
 */
 showEditParametersetPeriod:function(index){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPeriodBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_periods[index]);
    app.parametersetPeriodBeforeEditIndex = index;

    app.current_parameter_set_period = app.$data.session.parameter_set.parameter_set_periods[index];

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetPeriodModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit parameter set periods
*/
hideEditParametersetPeriod:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_periods[app.parametersetPeriodBeforeEditIndex], app.parametersetPeriodBeforeEdit);
        app.parametersetPeriodBeforeEdit=null;
    }
},

/** update parameterset period settings
*/
sendUpdatePeriods(){
    
    app.working = true;
    app.cancelModal=false;
    app.sendMessage("update_parameterset_period", {"sessionID" : app.sessionID,
                                                    "formData" : app.current_parameter_set_period,});
},

/** handle result of updating parameter set period
*/
takeUpdatePeriods(messageData){

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
        $('#editParametersetPeriodModal').modal('hide');            
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/**
 * add or remove value from number of periods
 */
sendAddParameterSetPeriod(value){
    app.$data.working = true;
    app.sendMessage("add_parameterset_period", {"sessionID" : app.sessionID,
                                                 "value" : value,});
},

takeAddParameterSetPeriod(messageData){
    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {   
        app.session.parameter_set = messageData.status.parameter_set;      
    } 
},

