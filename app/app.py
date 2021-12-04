from flask import Flask
from flask_socketio import SocketIO
from flask import render_template
from pymongo import MongoClient


app = Flask(__name__, template_folder='./templates')
#app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

client = MongoClient('mongodb://localhost:27017')
db = client['C3WAT']
accounts = db['accounts']

@app.route('/', methods=['GET', 'POST'])
def sessions():  # put application's code here
    try:
        # Just have to put users here
        users = ['paul', 'chris', 'david', 'fuck']
        return render_template('session.html', data=users) 
    except Exception as e:
        return(str(e))

@app.route('/dm', methods=['GET', 'POST'])
def dms():
    print("here in the dms")
    return render_template('dm.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was recieved!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('recieved my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    # Listens to localhost:5000 by default
    socketio.run(app, debug=True)
