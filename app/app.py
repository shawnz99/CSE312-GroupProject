from flask import Flask
from flask_socketio import SocketIO
from flask import render_template

app = Flask(__name__, template_folder='./templates')
#app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions():  # put application's code here
    return render_template('session.html') 

def messageReceived(methods=['GET', 'POST']):
    print('message was recieved!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('recieved my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    # Listens to localhost:5000 by default
    socketio.run(app, debug=True)
