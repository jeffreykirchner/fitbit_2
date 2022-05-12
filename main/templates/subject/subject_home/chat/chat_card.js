sendChat(){

    if(this.working) return;
    if(this.chat_text.trim() == "") return;
    if(this.chat_text.trim().length > 500) return;
    
    this.working = true;
    app.sendMessage("chat", {"text" : this.chat_text.trim(),
                            });

    this.chat_text="";                   
},

/** take result of moving goods
*/
takeChat(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateChat(messageData);                        
    } 
    else
    {
        
    }
},

/** take updated data from goods being moved by another player
*    @param messageData {json} session day in json format
*/
takeUpdateChat(messageData){
    
    let result = messageData.status;
    let chat = result.chat;
    let session_player = this.session_player;


    if(session_player.chat.length >= 100)
        session_player.chat.shift();

    session_player.chat.push(chat);
    app.updateChatDisplay();
},


/** update chat displayed on the screen
 */
updateChatDisplay(){
    if(!this.session.enable_chat) return;

    this.chat_list_to_display=Array.from(this.session_player.chat);
},

