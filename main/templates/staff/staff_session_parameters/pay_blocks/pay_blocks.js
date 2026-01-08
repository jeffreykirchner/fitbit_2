/**
 * add or remove value from number of periods
 */
sendAddParameterSetPayBlock(value){
    app.working = true;
    app.sendMessage("add_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                   "value" : value,
                                                   });
},

/**
 * remove a specific pay block
 */
sendRemoveParameterSetPayBlock(payblock_id){
    app.working = true;
    app.sendMessage("remove_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                      "id" : app.current_parameter_set_pay_block.id,
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
    else
    {                     
        app.displayErrors(messageData.status.errors);
    } 
},

/**show edit paramter set
 */
showEditPayBlock:function(index){
    app.clearMainFormErrors();

    app.current_parameter_set_pay_block = Object.assign({}, app.session.parameter_set.parameter_set_pay_blocks[index]);

    app.editParametersetPayBlockModal.toggle();
},

/**show edit paramter set
 */
showEditPayBlockPayment:function(index1, index2){
    app.clearMainFormErrors();

    app.current_parameter_set_pay_block_payment = Object.assign({}, app.session.parameter_set.parameter_set_pay_blocks[index1].parameter_set_pay_block_payments[index2]);

    app.editParametersetPayBlockPaymentModal.toggle();
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

/**
 * add or remove value from number of periods
 */
sendUpdateParameterSetPayBlockPayment(){
    app.working = true;
    app.sendMessage("update_parameterset_pay_block_payment", {"sessionID" : app.sessionID,
                                                              "formData" : app.current_parameter_set_pay_block_payment,
                                                   });
},

/**
 * add or remove value from number of periods
 */
sendAddParameterSetPayBlockPayment(value, payblock_id){
    app.working = true;
    app.sendMessage("add_parameterset_pay_block_payment", {"sessionID" : app.sessionID,
                                                           "payblockID" : payblock_id,
                                                           "value" : value,
                                                   });
},

/**
 * add or remove value from number of periods
 */
sendCopyPreviousParameterSetPayBlock(payblock_id){
    app.working = true;
    app.sendMessage("copy_previous_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                             "payblockID" : payblock_id,                                                           
                                                   });
},

/**
* add or remove value from number of periods
*/
sendCopyForwardParameterSetPayBlock(payblock_id){
   app.working = true;
   app.sendMessage("copy_forward_parameterset_pay_block", {"sessionID" : app.sessionID,
                                                            "payblockID" : payblock_id,                                                           
                                                  });
},