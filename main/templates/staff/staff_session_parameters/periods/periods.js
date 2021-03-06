

/**show edit parameter set periods
 */
 showEditParametersetPeriod(index){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPeriodBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_periods[index]);
    app.parametersetPeriodBeforeEditIndex = index;

    app.current_parameter_set_period = app.session.parameter_set.parameter_set_periods[index];

    tinymce.get("id_notice_text").setContent(app.current_parameter_set_period.notice_text);

    app.editParametersetPeriodModal.toggle();
},

/** hide edit parameter set periods
*/
hideEditParametersetPeriod(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_periods[app.parametersetPeriodBeforeEditIndex], app.parametersetPeriodBeforeEdit);
        app.parametersetPeriodBeforeEdit=null;
    }
},

/** update parameterset period settings
*/
sendUpdatePeriods(){

    app.current_parameter_set_period.notice_text = tinymce.get("id_notice_text").getContent();
    
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
        app.editParametersetPeriodModal.hide();        
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
    app.working = true;
    app.sendMessage("add_parameterset_period", {"sessionID" : app.sessionID,
                                                "value" : value,
                                                "increment_period" : app.increment_period});
},

takeAddParameterSetPeriod(messageData){
    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {   
        app.session.parameter_set = messageData.status.parameter_set;      
    } 
},


/**show edit parameter set period payment
 */
 showEditParametersetPeriodPayment(index, index2){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPeriodPaymentBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_periods[index].parameter_set_period_payments[index2]);
    app.parametersetPeriodBeforeEditIndex = index;
    app.parametersetPeriodPaymentBeforeEditIndex = index2;

    app.current_parameter_set_period_payment = app.session.parameter_set.parameter_set_periods[index].parameter_set_period_payments[index2];

    app.editParametersetPeriodPaymentModal.toggle();
},

/** hide edit parameter set period payment
*/
hideEditParametersetPeriodPayment(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_periods[app.parametersetPeriodBeforeEditIndex].parameter_set_period_payments[app.parametersetPeriodPaymentBeforeEditIndex], app.parametersetPeriodPaymentBeforeEdit);
        app.parametersetPeriodPaymentBeforeEdit=null;
    }
},

/** update parameterset period settings
*/
sendUpdatePayment(){
    
    app.working = true;
    app.cancelModal=false;
    app.sendMessage("update_parameterset_period_payment", {"sessionID" : app.sessionID,
                                                           "formData" : app.current_parameter_set_period_payment,});
},

/** handle result of updating parameter set period payment
*/
takeUpdatePayment(messageData){

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
        app.editParametersetPeriodPaymentModal.hide();            
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** update copy parameter set period forward
*/
sendCopyForward(id){
    
    app.working = true;
    app.cancelModal=false;
    app.sendMessage("update_parameterset_period_copy_forward", {"sessionID" : app.sessionID,
                                                                "id" : id,});
},

/** handle result of updating parameter set period payment
*/
takeCopyForward(messageData){

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
    } 
},

/** send copy previous period into this one
*/
sendCopyPrevious(id){
    
    app.working = true;
    app.cancelModal=false;
    app.sendMessage("update_parameterset_period_copy_previous", {"sessionID" : app.sessionID,
                                                                 "id" : id,});
},

/** take result of copy previous
*/
takeCopyPrevious(messageData){

    if(messageData.status.value == "success")
    {
        app.session.parameter_set = messageData.status.parameter_set;       
    } 
},
