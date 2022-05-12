/**start the experiment
*/
start_experiment(){
    app.working = true;
    app.control_working = true;
    app.sendMessage("start_experiment", {});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartExperiment(messageData){
    app.control_working = false;
    app.takeGetSession(messageData.session);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateStartExperiment(messageData){
    app.control_working = false;
    app.takeGetSession(messageData.session);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetExperiment(messageData){
    app.control_working = false;
    app.takeGetSession(messageData.session);
},

/**reset experiment, remove all bids, asks and trades
*/
reset_experiment(){
    if (!confirm('Reset session? All activity will be removed.')) {
        return;
    }

    app.working = true;
    app.control_working = true;
    app.sendMessage("reset_experiment", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetExperiment(messageData){
    app.control_working = false;
    app.chat_list_to_display=[];
    app.takeGetSession(messageData.session);
},

resetConnections(){
    if (!confirm('Reset connection status?.')) {
        return;
    }

    app.working = true;
    app.control_working = true;
    app.sendMessage("reset_connections", {});
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetConnections(messageData){
    app.control_working = false;
    app.takeGetSession(messageData.session);
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetConnections(messageData){
    app.control_working = false;
    app.takeGetSession(messageData.session);
},

/**advance to next phase
*/
next_experiment_phase(){
   
    if (!confirm('Continue to the next phase of the experiment?')) {
        return;
    }    

    app.working = true;
    app.control_working = true;
    app.sendMessage("next_phase", {});
},

/** take next period response
 * @param messageData {json}
*/
takeNextPhase(messageData){

    app.control_working = false;
    
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

    app.control_working = false;
    
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

    app.working = true;
    app.control_working = true;
    app.sendMessage("end_early", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeEndEarly(messageData){
    app.control_working = false;
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

    app.sendMessageModalForm.subject = app.session.invitation_subject;
    app.sendMessageModalForm.text = app.session.invitation_text;

    tinymce.get("id_invitation_subject").setContent(this.sendMessageModalForm.text);

    app.sendMessageModal.toggle();
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
    app.control_working = true;

    app.sendMessage("fill_with_test_data",
                   {});
},

/**
 * fill with test data
 */
 takeFillWithTestData(){
    app.control_working = false;
    if(messageData.status.value == "success")
    {         
        this.session.session_players = messageData.status.session_players;
    } 
    else
    {
       
    } 
},