from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

database = {
    "users": []
}



# loads homepage
@app.route('/')
def home():  # put application's code here
    users = ["andy", "ryan", "shawn", "kevin"]
    return render_template('home.html', users=users)


# receive websocket from event
@socketio.on('connection')
def handle_my_custom_event(json_data):
    print('received json: ' + json_data)
    print(request.sid)
    database["users"] += request.sid

# receive direct message and send to user
@socketio.on('send_msg')
def handle_my_custom_event(json_data):
    print('received json: ' + json_data)
    data = json.loads(json_data)
    send_data = json.dumps({'sender': request.sid, 'msg': data["msg"]})
    print(send_data)
    send_to = database["users"][-1] #would get from data["username"]
    emit("receive_msg", send_data, to=request.sid)


if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", "8002", debug=True)

# if __name__ == '__main__':
#   app.run("0.0.0.0", "8002", "debug")
