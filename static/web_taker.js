$(document).ready(function() {
    Plivo.onWebrtcNotSupported = webrtcNotSupportedAlert;
    Plivo.onReady = onReady;
    Plivo.init();
    Plivo.setDebug(true);

    var username = 'elricl140620163139';
    var pass = 'theoracle';
    Plivo.conn.login(username, pass);

    function webrtcNotSupportedAlert() {
        console.log("NOT SUPPORTED");
    }

    function onReady() {
        console.log("READY");
    }

    function onLogin() {
        console.log("Logged in");
    }

    function onIncomingCall(callerName, extraHeaders) {
        console.log("call recieved", extraHeaders);
        console.log(callerName);
        Plivo.conn.answer()
    }

    Plivo.onLogin = onLogin;

});
