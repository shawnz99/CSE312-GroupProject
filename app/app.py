from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
import json
import bcrypt
import os
from pymongo import MongoClient

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = '59dadf181b39480eae2b277c981bfbda'
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
socketio = SocketIO(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['C3WAT']
accounts = db['accounts']

database = {
    "users": []
}
# Homepage; DM's work in progress
@app.route('/')
def home():
    if 'username' in session:
        users = ["andy", "ryan", "shawn", "kevin"]
        user = accounts.find_one({'username': session['username']})
        return render_template('home.html', users=users, img=user['picturePath'])
    else:
        return render_template('index.html')
# Login Implementation
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # Compares submitted password to hash in DB
        if accounts.find_one({'username' : username}):
            login_user = accounts.find_one({'username': username})
            plain_password = request.form['password'].encode('utf8')
            hashed_password = login_user['password']
            if bcrypt.checkpw(plain_password, hashed_password):
                session['username'] = username
                print("Setting session username: " + username)
                flash('Successfully logged in!')
                return redirect(url_for('home'))
            else:
                flash('Wrong password.')
                return redirect(url_for('login'))
        else:
            flash('Wrong username.')
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('login.html')
# Register implementation
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if accounts.find_one({'username': username}):
            flash('Username already exists.')
            return redirect(url_for('register'))
        else:
            plain_password = request.form['password'].encode('utf8')
            hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
            account = {
                'username': username,
                'password': hashed_password,
                'picturePath': 'uploads/default.png'
            }
            if accounts.insert_one(account).inserted_id:
                flash('Account has been created!')
                return redirect(url_for('login'))
            else:
                flash('There was an error creating your account.')
                return redirect(url_for('register'))
    elif request.method == 'GET':
        return render_template('register.html')
# Logout implementation
@app.route('/logout', methods=['GET'])
def logout():
    print("Clearing session.")
    session.clear()
    return redirect(url_for('home'))

# Helper function for image upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File upload code source: https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' in session:
        if request.method == 'POST':
            # Error checking for file upload
            if 'file' not in request.files:
                flash('Image upload failed.')
                return redirect(url_for('settings'))
            file = request.files['file']
            if file.filename == '':
                flash("No image uploaded.")
                return redirect(url_for('settings'))
            # Save image to server directory and update the path in DB
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                accounts.update_one({'username': session['username']}, {'$set': {'picturePath': "uploads/"+filename}})
                return redirect(url_for('settings'))
        elif request.method == 'GET':
            user = accounts.find_one({'username': session['username']})
            return render_template('settings.html', img=user['picturePath'])
    else:
        flash('Please login to view this page.')
        return redirect(url_for('home'))

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

@app.route('/dm', methods=['GET', 'POST'])
def dms():
    print("here in the dms")
    return render_template('dm.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was recieved!!!')

if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", "8002", debug=True)

# if __name__ == '__main__':
#   app.run("0.0.0.0", "8002", "debug")
    # Listens to localhost:5000 by default
    #socketio.run(app, debug=True)
