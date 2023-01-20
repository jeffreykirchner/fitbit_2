/**send download summary data
*/
downloadSummaryData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_summary_data", {});
},

/** take download summary data
 * @param messageData {json}
*/
takeDownloadSummaryData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Summary_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download summary data
*/
downloadHeartRateData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_heart_rate_data", {});
},

/** take download summary data
 * @param messageData {json}
*/
takeDownloadHeartRateData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Heart_Rate_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download recruiter data
*/
downloadActivityData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_activities_data", {});
},

/** take download recruiter data
 * @param messageData {json}
*/
takedownloadActivityData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Activity_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download payment data
*/
downloadChatData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_chat_data", {});
},

/** take download payment data
 * @param messageData {json}
*/
takeDownloadChatData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Chat_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/** send request to pull time series data
*/
sendPullTimeSeriesData(){

    app.working = true;
    app.time_series_pulled = false;
    app.data_downloading = true;
    app.sendMessage("pull_time_series_data",
                   {});
},

/**
 * take result of senddPullTimeSeriesData
 */
takesPullTimeSeriesData(messageData)
{
    if(messageData.status.value == "success")
    { 
        app.time_series_pulled = true;
        app.data_downloading = false;
    }
    else
    {

    }
},

/**send download payment data
*/
downloadPayblockData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_payblock_data", {});
},

/** take download payment data
 * @param messageData {json}
*/
takeDownloadPayblockData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Fitbit_2_Payblock_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

