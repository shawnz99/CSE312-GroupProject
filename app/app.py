from flask import Flask, render_template, request
import bcrypt
from flask_socketio import SocketIO
from pymongo import MongoClient



client = MongoClient('mongodb://localhost:27017/')
db = client['C3WAT']
accounts = db['accounts']

app = Flask(__name__, template_folder='./templates')
#app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

# @app.route('/')
# def home():
#    return render_template('index.html')

@app.route('/login')
def login():
    return "Login"

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
    
if __name__ == '__main__':
    # Listens to localhost:5000 by default
    socketio.run(app, debug=True)
