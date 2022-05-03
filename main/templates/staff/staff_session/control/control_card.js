/**start the experiment
*/
start_experiment(){
    app.$data.working = true;
    app.sendMessage("start_experiment", {});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetExperiment(messageData){
    app.takeGetSession(messageData);
},

/**reset experiment, remove all bids, asks and trades
*/
reset_experiment(){
    if (!confirm('Reset session? All activity will be removed.')) {
        return;
    }

    app.$data.working = true;
    app.sendMessage("reset_experiment", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetExperiment(messageData){
    app.chat_list_to_display=[];
    app.takeGetSession(messageData);
},

resetConnections(){
    if (!confirm('Reset connection status?.')) {
        return;
    }

    app.$data.working = true;
    app.sendMessage("reset_connections", {});
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetConnections(messageData){
    app.takeGetSession(messageData);
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetConnections(messageData){
    app.takeGetSession(messageData);
},

/**advance to next phase
*/
next_experiment_phase(){
   
    if (!confirm('Continue to the next phase of the experiment?')) {
        return;
    }    

    app.$data.working = true;
    app.sendMessage("next_phase", {});
},

/** take next period response
 * @param messageData {json}
*/
takeNextPhase(messageData){
    
    if(messageData.status.value == "success")
    {
        this.session.current_experiment_phase = messageData.status.current_experiment_phase;
        this.session.finished = messageData.status.finished;
        this.updatePhaseButtonText();
    }
    else
    {

    }

},

/** take next period response
 * @param messageData {json}
*/
takeUpdateNextPhase(messageData){
    
    if(messageData.status.value == "success")
    {
        this.session.current_experiment_phase = messageData.status.current_experiment_phase;
        this.session.finished = messageData.status.finished;
        this.updatePhaseButtonText();
    }
    else
    {

    }
},


/**reset experiment, remove all bids, asks and trades
*/
endEarly(){
    if (!confirm('End the experiment after this period completes?')) {
        return;
    }

    app.$data.working = true;
    app.sendMessage("end_early", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeEndEarly(messageData){
    this.session = messageData.status.session;
},

/** send invitations
*/
sendSendInvitations(){

    this.sendMessageModalForm.text = tinymce.get("id_invitation_subject").getContent();

    if(this.sendMessageModalForm.subject == "" || this.sendMessageModalForm.text == "")
    {
        this.emailResult = "Error: Please enter a subject and email body.";
        return;
    }

    this.cancelModal = false;
    this.working = true;
    this.emailResult = "Sending ...";

    app.sendMessage("send_invitations",
                   {"formData" : this.sendMessageModalForm});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeSendInvitations(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {           
        this.emailResult = "Result: " + messageData.status.result.email_result.mail_count.toString() + " messages sent.";

        this.session.invitation_subject = messageData.status.result.invitation_subject;
        this.session.invitation_text = messageData.status.result.invitation_text;
    } 
    else
    {
        this.emailResult = messageData.status.result;
    } 
},

/** show edit subject modal
*/
showSendInvitations(){

    app.cancelModal=true;

    app.$data.sendMessageModalForm.subject = app.$data.session.invitation_subject;
    app.$data.sendMessageModalForm.text = app.$data.session.invitation_text;

    tinymce.get("id_invitation_subject").setContent(this.$data.sendMessageModalForm.text);
    
    var myModal = new bootstrap.Modal(document.getElementById('sendMessageModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit subject modal
*/
hideSendInvitations(){
    this.emailResult = "";
},

/**
 * fill invitation with default values
 */
fillDefaultInvitation(){
    this.sendMessageModalForm.subject = this.emailDefaultSubject;
    
    tinymce.get("id_invitation_subject").setContent(this.emailDefaultText);
},

/**
 * fill with test data
 */
fillWithTestData(){
    this.cancelModal = false;
    this.working = true;

    app.sendMessage("fill_with_test_data",
                   {});
},

/**
 * fill with test data
 */
 takeFillWithTestData(){
    if(messageData.status.value == "success")
    {         
        this.session.session_players = messageData.status.session_players;
    } 
    else
    {
       
    } 
},