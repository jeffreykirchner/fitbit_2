
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
                    software_version : "{{parameters.software_version}}",
                    playerKey : "{{session_player.player_key}}",
                    owner_color : 0xA9DFBF,
                    other_color : 0xD3D3D3,
                    session_player : {{session_player_json|safe}}, 
                    session : {{session_json|safe}},

                    end_game_form_ids: {{end_game_form_ids|safe}},

                    chat_text : "",
                    chat_recipients : "all",
                    chat_recipients_index : 0,
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
                case "update_end_game":
                    app.takeEndGame(messageData);
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
                case "survey_complete":
                    app.takeCheckIn(messageData);
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
               app.updateGraph();
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


                // if game is finished show modal
                if(app.$data.session.finished)
                {
                    this.showEndGameModal();
                }
            }

            if(this.session.current_experiment_phase == 'Instructions')
            {
                setTimeout(this.processInstructionPage, 1000);
                this.instructionDisplayScroll();
            }
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

            this.production_slider_one = 50;
            this.production_slider_two = 50;
            this.production_slider = 0;
            this.avatar_choice_grid_selected_row = 0;
            this.avatar_choice_grid_selected_col = 0;

            $('#endGameModal').modal('hide');
        },

        /**
         * show the end game modal
         */
        showEndGameModal(){
            if(this.end_game_modal_visible) return;

            //show endgame modal
            var myModal = new bootstrap.Modal(document.getElementById('endGameModal'), {
                keyboard: false
                })
            
            myModal.toggle();

            this.end_game_modal_visible = true;
        },

         /**
         * take end of game notice
         */
        takeEndGame(messageData){

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
            $('#avatarChoiceGridModal').modal('hide');
            $('#endGameModal').modal('hide');

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
    
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(var item in this.session)
            {
                $("#id_" + item).attr("class","form-control");
                $("#id_errors_" + item).remove();
            }

            s = this.session_player_move_two_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = this.session_player_move_three_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = this.end_game_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }
        },

        /** display form error messages
        */
        displayErrors(errors){
            for(var e in errors)
            {
                $("#id_" + e).attr("class","form-control is-invalid")
                var str='<span id=id_errors_'+ e +' class="text-danger">';
                
                for(var i in errors[e])
                {
                    str +=errors[e][i] + '<br>';
                }

                str+='</span>';
                $("#div_id_" + e).append(str); 

                var elmnt = document.getElementById("div_id_" + e);
                elmnt.scrollIntoView(); 

            }
        }, 

        /**
         * return session player that has specified id
         */
        findSessionPlayer(id){

            let session_players = app.$data.session.session_players;
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

            let session_players = app.$data.session.session_players;
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

        $('#moveTwoGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
        $('#moveThreeGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
        $('#avatarChoiceGridModal').on("hidden.bs.modal", this.hideChoiceGridModal);
        $('#endGameModal').on("hidden.bs.modal", this.hideEndGameModal);
        {%if session.parameter_set.test_mode%} setTimeout(this.doTestMode, this.randomNumber(1000 , 10000)); {%endif%}

        window.addEventListener('resize', this.updateGraph);

    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  