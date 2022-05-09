
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    helpText : "Loading ...",
                    sessionID : {{session.id}},
                    session : null, {{session_json|safe}}                  
                    valuecost_modal_label:'Edit Value or Cost',

                    current_parameter_set_player : {},  //{{first_parameter_set_player_json|safe}}
                    current_parameter_set_period : {}, //{{first_parameter_set_period_json|safe}}
                    current_parameter_set_period_payment : {},  //{{first_parameter_set_period_payment_json|safe}}
                    current_parameter_set_zone_minutes : {},  //{{first_parameter_set_zone_minutes_json|safe}}               

                    parameterset_form_ids: {{parameterset_form_ids|safe}},
                    parameterset_player_form_ids: {{parameterset_player_form_ids|safe}},
                    parameterset_period_form_ids: {{parameterset_period_form_ids|safe}},
                    parameterset_zone_minutes_form_ids: {{parameterset_zone_minutes_form_ids|safe}},

                    upload_file: null,
                    upload_file_name:'Choose File',
                    uploadParametersetButtonText:'Upload  <i class="fas fa-upload"></i>',
                    uploadParametersetMessaage:'',
                    import_parameters_message : "",

                    increment_period : "1",
                    increment_player : "1",

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
                case "update_session":
                    app.takeUpdateSession(messageData);
                    break;
                case "update_parameterset":
                    app.takeUpdateParameterset(messageData);
                    break;        
                case "update_parameterset_player":
                    app.takeUpdateParametersetPlayer(messageData);
                    break;     
                case "remove_parameterset_player":
                    app.takeRemoveParameterSetPlayer(messageData);
                    break;
                case "add_parameterset_player":
                    app.takeAddParameterSetPlayer(messageData);
                    break;     
                case "add_parameterset_period":
                    app.takeAddParameterSetPeriod(messageData);
                    break;   
                case "update_parameterset_period":
                    app.takeUpdatePeriods(messageData);
                    break; 
                case "update_parameterset_period_copy_forward":
                    app.takeCopyForward(messageData);
                    break;
                case "update_parameterset_period_copy_previous":
                    app.takeCopyPrevious(messageData);
                    break;
                case "update_parameterset_period_payment":
                    app.takeUpdatePayment(messageData);
                    break;
                case "add_parameterset_zone_minutes":
                    app.takeAddParameterSetZoneMinutes(messageData);
                    break;   
                case "update_parameterset_zone_minutes":
                    app.takeUpdateZoneMinutes(messageData);
                    break;     
                case "import_parameters":
                    app.takeImportParameters(messageData);
                    break;
                case "download_parameters":
                    app.takeDownloadParameters(messageData);
                    break;
                case "help_doc":
                    app.takeLoadHelpDoc(messageData);
                    break;
            }

            app.$data.first_load_done = true;

            app.working = false;
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage(messageType, messageText) {
            

            app.$data.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.session = messageData.session;

            if(app.session.started)
            {
                
            }
            else
            {
                
            }                     
        },

        /** send winsock request to get session info
        */
        sendGetSession(){
            app.sendMessage("get_session",{"sessionID" : app.$data.sessionID});
        },

        /** send session update form   
        */
        sendUpdateSession(){
            app.$data.cancelModal = false;
            app.$data.working = true;
            app.sendMessage("update_session",{"formData" : $("#sessionForm").serializeArray(),
                                              "sessionID" : app.$data.sessionID});
        },

        /** take update session reponse
         * @param messageData {json} result of update, either sucess or fail with errors
        */
        takeUpdateSession(messageData){
            app.clearMainFormErrors();

            if(messageData.status == "success")
            {
                app.takeGetSession(messageData);       
                $('#editSessionModal').modal('hide');    
            } 
            else
            {
                app.$data.cancelModal=true;                           
                app.displayErrors(messageData.errors);
            } 
        },

        /**trucate text to 10 charcters with elipsis
         * @param text : string to be truncated
         */
        truncateText(text){

            var new_text = "";

            new_text = text.substring(0, 10);

            if(text.length>10)
            {
                new_text += "...";
            }

            return new_text;

        },

        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },

        {%include "staff/staff_session_parameters/general_settings/general_settings.js"%}
        {%include "staff/staff_session_parameters/control/control.js"%}
        {%include "staff/staff_session_parameters/players/players.js"%}
        {%include "staff/staff_session_parameters/periods/periods.js"%}
        {%include "staff/staff_session_parameters/zone_minutes/zone_minutes.js"%}
        {%include "js/help_doc.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(var item in app.$data.session)
            {
                $("#id_" + item).attr("class","form-control");
                $("#id_errors_" + item).remove();
            }

            s = app.parameterset_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.parameterset_player_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.parameterset_player_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.parameterset_period_form_ids;
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
    },

    mounted(){
        $('#editSessionModal').on("hidden.bs.modal", this.hideEditSession); 
        $('#importParametersModal').on("hidden.bs.modal", this.hideImportParameters); 
        $('#editParametersetModal').on("hidden.bs.modal", this.hideEditParameterset);
        $('#editParametersetPlayerModal').on("hidden.bs.modal", this.hideEditParametersetPlayer);
        $('#editParametersetPeriodModal').on("hidden.bs.modal", this.hideEditParametersetPeriod);
        $('#editParametersetZoneMinutesModal').on("hidden.bs.modal", this.hideEditParametersetPeriod);
        $('#editParametersetPeriodPaymentModal').on("hidden.bs.modal", this.hideEditParametersetPeriodPayment);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  