/**
 * get pay block the server
 */
get_pay_block(pay_block){
    this.working = true;
    this.payments_downloading = true;
    this.payments_copied = false;
    app.sendMessage("get_pay_block",{"pay_block" : pay_block});
},

/**
 * get pay block the server
 */
take_get_pay_block(messageData){    

    this.payments_downloading = false;
    // this.payments_copied = true;
    // if(messageData.status.value == "success")
    // {
    //     app.copyToClipboard(messageData.status.pay_block_csv);      
    // } 
    // else
    // {
        
    // } 

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.pay_block_csv]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Payment_Data_Session_" + app.session.id +"_Block_" + messageData.status.pay_block_number + ".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

//copy text to clipboard
copyToClipboard(text){

    // Create a dummy input to copy the string array inside it
    var dummy = document.createElement("textarea");

    // Add it to the document
    document.body.appendChild(dummy);

    // Set its ID
    dummy.setAttribute("id", "dummy_id");

    // Output the array into it
    document.getElementById("dummy_id").value=text;

    // Select it
    dummy.select();
    dummy.setSelectionRange(0, 99999); /*For mobile devices*/

    // Copy its contents
    document.execCommand("copy");

    // Remove it as its not needed anymore
    document.body.removeChild(dummy);

    /* Copy the text inside the text field */
    document.execCommand("copy");
},

