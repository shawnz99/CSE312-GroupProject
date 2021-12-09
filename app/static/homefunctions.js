var socket = io();
// Connected to server
socket.on( 'connect', function() {
    socket.emit( 'my event', {
        data: 'User Connected'
    } )

    /* Snags the messages */
    var form = $( '#form' ).on( 'submit', function( e ) {
        e.preventDefault()
        let user_name  = $( 'input.username' ).val()
        let user_input = $( 'input.message' ).val()

        user_input = charCheck(user_input);

        /*
         *   Sends messages to server,
         *   charCheck is HTML inj prevention
         */
        socket.emit( 'my event', {
            user_name : charCheck(user_name),
            message : charCheck(user_input)
        } )
        $( 'input.message' ).val( '' ).focus()
    } )
} )
socket.on( 'my response', function( msg ) {
    if( typeof msg.user_name !== 'undefined' ) {
        $( 'h3' ).remove()
        $( 'div.message_holder' ).append( '<div id='+msg.id+'><b style="color: #000">'+msg.user_name+': </b> '+msg.message+'  <button type="button" onclick=myFunction($(this).closest("div").attr("id")) > Like & subscribe </button> <p id=votes> Likes: </p> </div>' )
    }
})

/*
 * Updates the Votes counter with the new value
 */
socket.on('vote_update', (data) => {
    var doc = document.getElementById(data.div_id)
    doc.getElementsByTagName("p")[0].innerHTML = 'Likes: ' + data.votes;
})

/*
 *  Grabs the id of the message that had a vote
 *  on it and emits the id to server
 */
function myFunction(id) {
    id = parseInt(id);
    socket.emit( 'vote', id)
}

/*Blocks HTML injection */
function charCheck(msg) {
    if (msg.search("<") != -1 ) {
        msg = msg.replaceAll(/</g, '&lt');
    }

    if ( msg.search(">") != -1) {
        msg = msg.replaceAll(/>/g, '&gt');
    }

    return msg;
}

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