/**
 * send request to create new session
 */
sendCreateSession(){
    this.working = true;
    this.createSessionButtonText ='<i class="fas fa-spinner fa-spin"></i>';
    app.sendMessage("create_session",{});
},

/**
 * take crate a new session
 */
takeCreateSession(messageData){    
    this.createSessionButtonText ='Create Session <i class="fas fa-plus"></i>';
    app.takeGetSessions(messageData);
},

/**
 * send request to delete session
 * @param id : int
 */
sendDeleteSession(id){
    this.working = true;
    app.sendMessage("delete_session",{"id" : id});
},


/**
 * sort sessions by title
 */
sortByTitle:function(){

    app.working = true;

    app.sessions.sort(function(a, b) {
        a=a.title.trim().toLowerCase();
        b=b.title.trim().toLowerCase();
        return a < b ? -1 : a > b ? 1 : 0;
    });

    app.working = false;
},

/**
 * sort sessions by date
 */
sortByDate:function(){

    app.working = true;

    app.sessions.sort(function(a, b) {
        return new Date(b.start_date) - new Date(a.start_date);

    });

    app.working = false;
},