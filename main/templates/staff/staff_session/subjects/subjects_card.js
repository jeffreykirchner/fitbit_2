 /**
 * take update player groups
 * @param messageData {json} session day in json format
 */
  takeUpdateConnectionStatus(messageData){
            
    if(messageData.status.value == "success")
    {
        let result = messageData.status.result;
        let session_players = app.session.session_players;

        session_player = app.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.connected_count = result.connected_count;
        }
    }
},

/** take name and student id
* @param messageData {json} session day in json format
*/
takeUpdateName(messageData){
           
    if(messageData.status.value == "success")
    {
        let result = messageData.status.result;

        session_player = app.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.name = result.name;
            session_player.student_id = result.student_id;
        }       
    }
 },

/** take name and student id
* @param messageData {json} session day in json format
*/
takeNextInstruction(messageData){
           
    if(messageData.status.value == "success")
    {
        let result = messageData.status.result;

        session_player = this.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.current_instruction = result.current_instruction;
            session_player.current_instruction_complete = result.current_instruction_complete;
        }       
    }
 },

 /** take name and student id
* @param messageData {json} session day in json format
*/
takeFinishedInstructions(messageData){
           
    if(messageData.status.value == "success")
    {
        let result = messageData.status.result;

        session_player = this.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.instructions_finished = result.instructions_finished;
            session_player.current_instruction_complete = result.current_instruction_complete;
        }       
    }
 },

 /**
  * update subject earnings
  *  @param messageData {json} session day in json format
  */
 takeUpdateEarnings(messageData){

    if(messageData.status.value == "success")
    {
        let session_player_earnings = messageData.status.result.session_player_earnings;
        let session_players = this.session.session_players;

        for(let i=0; i<session_player_earnings.length; i++)
        {
            session_player = app.findSessionPlayer(session_player_earnings[i].id);

            if(session_player)
            {
                session_player.earnings = session_player_earnings[i].earnings;
            }
        }
    }
 },

 /**
  * return session player that has specified id
  */
 findSessionPlayer(id){

    let session_players = this.session.session_players;
    for(let i=0; i<session_players.length; i++)
    {
        if(session_players[i].id == id)
        {
            return session_players[i];
        }
    }

    return null;
 },

/**
 * return session player index that has specified id
 */
findSessionPlayerIndex(id){

    let session_players = app.session.session_players;
    for(let i=0; i<session_players.length; i++)
    {
        if(session_players[i].id == id)
        {
            return i;
        }
    }

    return null;
},

/** send session update form   
*/
sendEmailList(){
    this.cancelModal = false;
    this.working = true;

    app.sendMessage("email_list",
                   {"csv_data" : this.csv_email_list});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateEmailList(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {            
        app.uploadEmailModal.hide(); 
        app.session = messageData.status.result.session;
    } 
    else
    {
        
    } 
},

/** show edit subject modal
*/
showSendEmailList(){
    app.clearMainFormErrors();
    this.cancelModal=true;

    this.csv_email_list = "";
    
    app.uploadEmailModal.toggle();
},

/** hide edit subject modal
*/
hideSendEmailList(){
    this.csv_email_list = "";

    if(this.cancelModal)
    {      
       
    }
},

/** send subject update form   
*/
sendUpdateSubject(){
    this.cancelModal = false;
    this.working = true;
    app.sendMessage("update_subject",
                   {"formData" : this.staffEditNameEtcForm});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateSubject(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {            
        app.editSubjectModal.hide();   

        let session_player = app.findSessionPlayer(messageData.status.session_player.id);
        session_player.name = messageData.status.session_player.name;
        session_player.student_id = messageData.status.session_player.student_id;
        session_player.email = messageData.status.session_player.email;
        session_player.group_number = messageData.status.session_player.group_number;
        session_player.disabled = messageData.status.session_player.disabled;
        session_player.fitbit_user_id = messageData.status.session_player.fitbit_user_id;
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** send session update form   
*/
sendLoadFullSubject(id){
    this.working = true;
    app.sendMessage("load_full_subject",
                   {"subject_id" : id});
},

takeLoadFullSubject(messageData)
{
    for(i=0;i<app.session.session_players.length;i++)
    {
        if(app.session.session_players[i].id == messageData.status.session_player.id)
        {
            app.session.session_players[i] = messageData.status.session_player;
        }
    }

    app.updateChatDisplay();
},

/** show edit subject modal
*/
showEditSubject:function(id){

    if(!app.session.started) return;

    app.clearMainFormErrors();
    this.cancelModal=true;

    this.staffEditNameEtcForm.id = id;

    let session_player = app.findSessionPlayer(id);

    this.staffEditNameEtcForm.name = session_player.name;
    this.staffEditNameEtcForm.student_id = session_player.student_id;
    this.staffEditNameEtcForm.email = session_player.email;
    this.staffEditNameEtcForm.group_number = session_player.group_number;
    this.staffEditNameEtcForm.disabled = session_player.disabled ? 1 : 0;
    this.staffEditNameEtcForm.fitbit_user_id = session_player.fitbit_user_id;

    app.editSubjectModal.toggle();
},

/** hide edit subject modal
*/
hideEditSubject:function(){
    if(this.cancelModal)
    {
       
       
    }
},

/** show view subject modal
*/
showViewSubject:function(id, subject_id){
    
    app.sendLoadFullSubject(subject_id);

    app.current_subject = id;

    var myModal = new bootstrap.Modal(document.getElementById('viewSubjectModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** show view subject modal
*/
showViewSubjectChat:function(id, subject_id){

    app.sendLoadFullSubject(subject_id);
    
    app.current_subject = id;

    var myModal = new bootstrap.Modal(document.getElementById('viewSubjectChatModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/**
 * update chat
 */
updateChatDisplay(){            
    this.chat_list_to_display=this.session.session_players[app.current_subject].chat;
},

/** hide view subject modal
*/
hideViewSubject:function(){
    
},

/** send session update form   
*/
sendForceCheckIn(id){
    if (!confirm('Force check in?')) {
        return;
    }
    
    this.working = true;
    app.sendMessage("force_check_in",
                   {"id" : id});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeForceCheckIn(messageData){
   
    this.working = false;

    if(messageData.status.value == "success")
    {             
        app.session.session_players[app.current_subject] =  messageData.status.session_player;

        //session_player =  messageData.status.session_player;

        // for(i=0;i<session_player.session_player_periods.length;i++)
        // {
        //     if(session_player.session_player_periods[i].id == messageData.status.session_player_period.id)
        //     {
        //         session_player.session_player_periods[i] = messageData.status.session_player_period;
        //         break;
        //     }
        // }
    } 
    else
    {
        
    } 
},

/** take update consent form status
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateConsentForm(messageData){

    if(messageData.status.value == "success")
    {             
        let session_player = app.findSessionPlayer(messageData.status.result.player_id);

        if(session_player)
        {
            session_player.consent_form_required = messageData.status.result.consent_form_required;
        }
        
    } 
    else
    {
        
    } 
},

/**
 * get pay block the server
 */
get_playerlist_csv(){
    this.working = true;
    this.player_list_copied = false;
    app.sendMessage("get_playerlist_csv", {});
},


/**
 * get pay block the server
 */
take_playerlist_csv(messageData){    

    this.player_list_copied = true;

    if(messageData.status.value == "success")
    {
        app.copyToClipboard(messageData.status.player_list_csv);      
    } 
    else
    {
        
    } 
},

/** show edit subject modal
*/
showImportSession(){
    app.clearMainFormErrors();
    this.cancelModal=true;
    
    app.importSessionModal.toggle();
},

/** hide edit subject modal
*/
hideImportSession(){
    

    if(this.cancelModal)
    {      
       
    }
},

/**
 * get pay block the server
 */
import_session(){
    this.working = true;
    this.session_imported = false;
    app.sendMessage("import_session", {session_id:app.session_import});
},


/**
 * get pay block the server
 */
take_import_session(messageData){    

    this.session_imported = true;

    if(messageData.status.value == "success")
    {
        app.session.session_players = messageData.status.session_players;   
        app.importSessionModal.hide();   
    } 
    else
    {
        
    } 
},

 /** send anonymize data request to server
*/
send_anonymize_data(){
    
    if (!confirm('Anonymize data? Identifying information will be permanent removed.')) {
        return;
    }

    app.working = true;
    app.sendMessage("anonymize_data",{});
},

/** take anonymize data result for server
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_anonymize_data(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {            

        let session_player_updates = messageData.status.result;
        let session_players = app.session.session_players;

        for(let i=0; i<session_player_updates.length; i++)
        {
            session_player = app.findSessionPlayer(session_player_updates[i].id);

            if(session_player)
            {
                session_player.email = session_player_updates[i].email;
                session_player.name = session_player_updates[i].name;
                session_player.student_id = session_player_updates[i].student_id;
            }
        }
    
    } 
},