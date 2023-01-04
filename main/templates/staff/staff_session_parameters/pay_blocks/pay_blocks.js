/**
 * add or remove value from number of periods
 */
sendAddParameterSetPayBlock(value){
    app.working = true;
    app.sendMessage("add_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                   "value" : value,
                                                   });
},

takeUpdatePayBlock(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {   
        app.session.parameter_set = messageData.status.parameter_set;  
        
        app.editParametersetPayBlockModal.hide();
        app.editParametersetPayBlockPaymentModal.hide();
    } 
},

/**show edit paramter set
 */
showEditPayBlock:function(index){
    app.clearMainFormErrors();

    app.current_parameter_set_pay_block = Object.assign({}, app.session.parameter_set.parameter_set_pay_blocks[index]);

    app.editParametersetPayBlockModal.toggle();
},

/**
 * add or remove value from number of periods
 */
sendUpdateParameterSetPayBlock(){
    app.working = true;
    app.sendMessage("update_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                      "formData" : app.current_parameter_set_pay_block,
                                                   });
},