checkIn(){
    app.working = true;
    app.sendMessage("check_in", {});
},

takeCheckIn(){
    app.working = false;
},