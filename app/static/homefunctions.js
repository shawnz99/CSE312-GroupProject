var socket = io();
// Connected to server
socket.on('connect', function() {
    socket.emit('connection', JSON.stringify({'data': 'I\'m connected!'}));
});

socket.on('receive_msg', function(data){
    receiveMessage(data)
});


function sendMessage(user) {
    const dmBox = document.getElementById("dm_" + user);
    const msg = dmBox.value;
    dmBox.value = "";
    //dmBox.focus();
    if(msg !== "") {
        socket.emit('send_msg', JSON.stringify({'username': user, 'msg': msg}));
    }
}

function receiveMessage(json_data) {
    const data = JSON.parse(json_data);
    alert(data["sender"] + ": " + data["msg"]);
}