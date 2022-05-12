
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    is_subject : true,
                    working : false,
                    first_load_done : false,                       //true after software is loaded for the first time
                    helpText : "Loading ...",
                    software_version : "{{parameters.software_version}}",
                    playerKey : "{{session_player.player_key}}",
                    owner_color : 0xA9DFBF,
                    other_color : 0xD3D3D3,
                    session_player : null, 
                    session : null,

                    end_game_form_ids: {{end_game_form_ids|safe}},

                    chat_text : "",
                    chat_button_label : "Everyone",
                    chat_list_to_display : [],                //list of chats to display on screen

                    end_game_modal_visible : false,
                    avatar_choice_modal_visible : false,

                    instruction_pages : {{instruction_pages|safe}},

                    check_in_error_message : "",
                    show_fitbit_connect : false,
                    fitbit_error_message : "",

                    //graph globals
                    marginY : 80,
                    marginX : 75,
                    margin2 : 35,
                    sizeW : 0,
                    sizeH : 0,

                    endGameModal : null,
                    consentModal : null,

                }},
    methods: {

        /** fire when websocket connects to server
        */
        handleSocketConnected(){            
            app.sendGetSession();
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            messageType = data.message.messageType;
            messageData = data.message.messageData;

            switch(messageType) {                
                case "get_session":
                    app.takeGetSession(messageData);
                    break; 
                case "update_start_experiment":
                    app.takeUpdateStartExperiment(messageData);
                    break;
                case "update_reset_experiment":
                    app.takeUpdateResetExperiment(messageData);
                    break;
                case "chat":
                    app.takeChat(messageData);
                    break;
                case "update_chat":
                    app.takeUpdateChat(messageData);
                    break;
                case "name":
                    app.takeName(messageData);
                    break;
                case "update_next_phase":
                    app.takeUpdateNextPhase(messageData);
                    break;
                case "next_instruction":
                    app.takeNextInstruction(messageData);
                    break;
                case "finish_instructions":
                    app.takeFinishInstructions(messageData);
                    break;
                case "check_in":
                    app.takeCheckIn(messageData);
                    break;
                case "update_check_in":
                    app.takeCheckInUpdate(messageData);
                    break;
                case "survey_complete":
                    app.takeSurveyComplete(messageData);
                    break;
                case "help_doc_subject":
                    app.takeLoadHelpDoc(messageData);
                    break;
                case "consent_form":
                    app.takeConsentForm(messageData);
                    break;
                
            }

            this.first_load_done = true;

            this.working = false;
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage(messageType, messageText) {            

            this.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /** send winsock request to get session info
        */
        sendGetSession(){
            app.sendMessage("get_session", {"playerKey" : this.playerKey, "first_load_done" : this.first_load_done});
        },
        
        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.session = messageData.status.session;
            app.session_player = messageData.status.session_player;
            app.show_fitbit_connect = messageData.status.show_fitbit_connect;
            app.fitbit_error_message =  messageData.status.fitbit_error_message;

            if(app.session.started)
            {
                setTimeout(app.updateGraph, 250);
            }
            else
            {
                
            }                
            
            if(this.session.current_experiment_phase != 'Done')
            {
                                
                if(this.session.current_experiment_phase != 'Instructions')
                {
                    app.updateChatDisplay();               
                }

            }

            if(!app.first_load_done)
            {
                // setTimeout(function(){
                //             document.getElementById("id_graph_card").scrollIntoView();
                //            }, 
                //            500);
            }

            if(this.session.current_experiment_phase == 'Instructions')
            {
                setTimeout(this.processInstructionPage, 1000);
                this.instructionDisplayScroll();
            }

            if(!app.first_load_done)
            {
                setTimeout(app.doFirstLoad, 500);
            }
        },

        doFirstLoad()
        {

            app.endGameModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('endGameModal'), {keyboard: false})
            app.consentModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('consentModal'), {keyboard: false})

            document.getElementById('endGameModal').addEventListener('hidden.bs.modal', app.hideEndGameModal);

            {%if session.parameter_set.test_mode%} setTimeout(this.doTestMode, this.randomNumber(1000 , 10000)); {%endif%}
    
            window.addEventListener('resize', this.updateGraph);

            if(app.session_player.consent_form_required)
            {
                app.showConsentForm();
            }
        },

        /**
         * send request for help doc
         * @param title : string
         */
        sendLoadHelpDocSubject(title){
            this.working = true;
            this.helpText = "Loading ...";

            var myModal = new bootstrap.Modal(document.getElementById('helpModal'), {
                keyboard: false
                })

            myModal.toggle();

            app.sendMessage("help_doc_subject", {title : title});
        },

        /** update start status
        *    @param messageData {json} session day in json format
        */
        takeUpdateStartExperiment(messageData){
            app.takeGetSession(messageData);
        },

        /** update reset status
        *    @param messageData {json} session day in json format
        */
        takeUpdateResetExperiment(messageData){
            app.takeGetSession(messageData);

            app.endGameModal.hide();
        },

        showConsentForm(){
            app.consentModal.toggle();
        },

        /**
        * send accept consent form
        */
        sendConsentForm(){
            this.working = true;
            app.sendMessage("consent_form", {});
        },
        
        /** take result of consent form
        *    @param messageData {json} session day in json format
        */
        takeConsentForm(messageData){
            app.session_player.consent_form_required = messageData.status.result.consent_form_required; 
            app.consentModal.hide();
        },

        takeSurveyComplete(messageData){

            if(messageData.status.value == "success")
            {
                app.session_player = messageData.status.result.session_player;
            }
            else
            {
                
            }
        },


        /** take next period response
         * @param messageData {json}
        */
        takeUpdateNextPhase(messageData){

            app.endGameModal.hide();

            this.session.current_experiment_phase = messageData.status.session.current_experiment_phase;
            this.session.session_players = messageData.status.session_players;
            this.session_player = messageData.status.session_player;

            app.updateChatDisplay();          
        },

        /** hide choice grid modal modal
        */
        hideEndGameModal(){
            this.end_game_modal_visible=false;
        },

        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },
        
        {%include "subject/subject_home/chat/chat_card.js"%}
        {%include "subject/subject_home/connect/connect_card.js"%}
        {%include "subject/subject_home/checkin/checkin_card.js"%}
        {%include "subject/subject_home/test_mode/test_mode.js"%}
        {%include "subject/subject_home/instructions/instructions_card.js"%}
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "js/help_doc.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(var item in app.session)
            {
                e = document.getElementById("id_errors_" + item);
                if(e) e.remove();
            }

            s = this.end_game_form_ids;
            for(var i in s)
            {
                e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }
        },

        /** display form error messages
        */
        displayErrors(errors){
            for(var e in errors)
                {
                    //e = document.getElementById("id_" + e).getAttribute("class", "form-control is-invalid")
                    var str='<span id=id_errors_'+ e +' class="text-danger">';
                    
                    for(var i in errors[e])
                    {
                        str +=errors[e][i] + '<br>';
                    }

                    str+='</span>';

                    document.getElementById("div_id_" + e).insertAdjacentHTML('beforeend', str);
                    document.getElementById("div_id_" + e).scrollIntoView();
                }
        }, 

        /**
         * return session player that has specified id
         */
        findSessionPlayer(id){

            let session_players = app.session.session_players;
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

    },

    mounted(){

    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  