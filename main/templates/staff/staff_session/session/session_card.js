/** send session update form   
*/
sendUpdateSession(){
    this.cancelModal = false;
    this.working = true;
    app.sendMessage("update_session",{"formData" : {title:app.session.title, start_date:app.session.start_date_widget}});
},

/** take update session reponse
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateSession(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData.status.session);       
        app.editSessionModal.hide();    
    } 
    else
    {
        this.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** show edit session modal
*/
showEditSession:function(){
    app.clearMainFormErrors();
    this.cancelModal=true;
    this.sessionBeforeEdit = Object.assign({}, this.session);

    app.editSessionModal.toggle();
},

/** hide edit session modal
*/
hideEditSession:function(){
    if(this.cancelModal)
    {
        Object.assign(this.session, this.sessionBeforeEdit);
        this.sessionBeforeEdit=null;
    }
},