# X On the homepage of the app, display a list of currently logged in users. 
# X Next to each user in the list is an option to send them a DM. When a DM is sent to a user, 
# X (kinda) a JavaScript alert appears containing the message and the username of the sender. 
# Since that user has an option to send a DM to this user from their list,the option to reply exists
# On the homepage of the app, provide an area where users can post text messages. 
# Users can click a button to upvote each post via WebSockets which can be seen by all users without a refresh
# Users can create an account and upload a profile picture (which they can change). 
# In the list of currently logged in users, display each users’ profile picture

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import json
import bcrypt
from pymongo import MongoClient


# app.config['SECRET_KEY'] = 'secret!'

app = Flask(__name__, template_folder='./templates')
#app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

database = {
    "users": []
}

client = MongoClient('mongodb://localhost:27017/')
db = client['C3WAT']
accounts = db['accounts']

# loads homepage
@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    users = ["andy", "ryan", "shawn", "kevin"]
    return render_template('session.html', users=users)

# @app.route('/')
# def home():
#    return render_template('index.html')

@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        print('TESTING!')

        if accounts.find_one({'username' : username}):
            login_user = accounts.find_one({'username': username})
            plain_password = request.form['password'].encode('utf8')
            hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
            print('Hashed Password = ' + hashed_password)
            print('Database Password = ' + login_user['password'])
            if hashed_password == login_user['password']:
                msg = 'Succesfully logged in!'
                return render_template('login.html', msg = msg)
        else:
            msg = 'Username was not found!'
            return render_template('login.html', msg = msg)

    elif request.method == 'GET':
        return render_template('login.html')



#@app.route('/', methods=['GET', 'POST'])
#def sessions():  # put application's code here
#    try:
#        # Just have to put users here
#        users = ['paul', 'chris', 'david', 'fuck']
#        return render_template('session.html', data=users) 
#    except Exception as e:
#        return(str(e))

@app.route('/dm', methods=['GET', 'POST'])
def dms():
    users = ["andy", "ryan", "shawn", "kevin"]
    return render_template('home.html', users=users)

def messageReceived(methods=['GET', 'POST']):
    print('message was recieved!!!')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']

        if accounts.find_one({'username': username}):
            msg = 'Username already exists.'
        else:
            plain_password = request.form['password'].encode('utf8')
            hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
            account = {
                'username': username,
                'password': hashed_password
            }
            if accounts.insert_one(account).inserted_id:
                msg = 'Account has been created!'
            else:
                msg = 'There was an error creating your account.'
        
        return render_template('register.html', msg=msg)
    elif request.method == 'GET':
        return render_template('register.html')
      
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
    
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('recieved my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@socketio.on('vote')
def handle_event():
    print('here')

    
if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", "8002", debug=True)

# if __name__ == '__main__':
#   app.run("0.0.0.0", "8002", "debug")
    # Listens to localhost:5000 by default
    #socketio.run(app, debug=True)
