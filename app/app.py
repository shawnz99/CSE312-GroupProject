#
# [X] On the homepage of the app, display a list of currently logged in users. 
# [X] Next to each user in the list is an option to send them a DM. When a DM is sent to a user, 
# [X] a JavaScript alert appears containing the message and the username of the sender. 
# [X] Since that user has an option to send a DM to this user from their list,the option to reply exists
# [ ] On the homepage of the app, provide an area where users can post text messages. 
# [ ] Users can click a button to upvote each post via WebSockets which can be seen by all users without a refresh
# [X] Users can create an account and upload a profile picture (which they can change). 
# [X] In the list of currently logged in users, display each users’ profile picture
#
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
import json
import bcrypt
import os
import secrets
from pymongo import MongoClient

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



app = Flask(__name__, template_folder='./templates')
# Set-Cookie options
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
app.config['SECRET_KEY'] = '59dadf181b39480eae2b277c981bfbda'
app.config['UPLOAD_FOLDER'] = '/app/static/uploads'
socketio = SocketIO(app, logger=True)

client = MongoClient('mongo')
db = client['C3WAT']
accounts = db['accounts']
votes = {}
id = 0 ## This is for the chat so there is a id for each message to grab for the upvotes


# Adding security headers to all responses

@app.after_request
def apply_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Homepage; DM's work in progress
@app.route('/')
def home():
    if 'username' in session:
        user = accounts.find_one({'username': session['username']})
        if user:
            users = accounts.find({'username': {'$ne': session['username']}, 'loggedIn': 'true'})
            return render_template('home.html', users=users, img=user['picturePath'])
        else:
            print("Clearing session.")
            session.clear()
            return redirect(url_for('home'))
    else:
        return render_template('index.html')

# Verify xsrf_token function
def verify_xsrf_token(xsrf_token):
    if xsrf_token == session['xsrf_token']:
        return True
    else:
        return False

# Login Implementation
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Check xsrf token
        if not verify_xsrf_token(request.form['xsrf_token']):
            flash('Invalid XSRF Token')
            return redirect(url_for('login'))
        username = request.form['username']
        # Compares submitted password to hash in DB
        if accounts.find_one({'username' : username}):
            login_user = accounts.find_one({'username': username})
            plain_password = request.form['password'].encode('utf8')
            hashed_password = login_user['password']
            if bcrypt.checkpw(plain_password, hashed_password):
                session['username'] = username
                accounts.update_one({'username': username}, {'$set': {'loggedIn': 'true'}})
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
        xsrf_token = secrets.token_urlsafe(32)
        session['xsrf_token'] = xsrf_token
        return render_template('login.html', xsrf_token=xsrf_token)



#@app.route('/', methods=['GET', 'POST'])
#def sessions():  # put application's code here
#    try:
#        # Just have to put users here
#        users = ['paul', 'chris', 'david', 'fuck']
#        return render_template('session.html', data=users)
#    except Exception as e:
#        return(str(e))


# Register implementation
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Check xsrf token
        if not verify_xsrf_token(request.form['xsrf_token']):
            flash('Invalid XSRF Token')
            return redirect(url_for('register'))
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
                'picturePath': 'uploads/default.png',
                'loggedIn': 'false'
            }
            if accounts.insert_one(account).inserted_id:
                flash('Account has been created!')
                return redirect(url_for('register'))
            else:
                flash('There was an error creating your account.')
                return redirect(url_for('register'))
    elif request.method == 'GET':
        xsrf_token = secrets.token_urlsafe(32)
        session['xsrf_token'] = xsrf_token
        return render_template('register.html', xsrf_token=xsrf_token)

# Logout implementation
@app.route('/logout', methods=['GET'])
def logout():
    print("Clearing session.")
    accounts.update_one({'username': session['username']}, {'$set': {'loggedIn': 'false'}, '$unset': {'sid': 1}})
    session.clear()
    flash('Successfully logged out.')
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
                print(os.getcwd())
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                accounts.update_one({'username': session['username']}, {'$set': {'picturePath': "uploads/"+filename}})
                return redirect(url_for('settings'))
        elif request.method == 'GET':
            user = accounts.find_one({'username': session['username']})
            return render_template('settings.html', img=user['picturePath'])
    else:
        flash('Please login to view this page.')
        return redirect(url_for('home'))

# Update user's socket id every connection
@socketio.on('connect')
def connect(json_data):
    print("Connecting session")
    if 'username' in session:
        accounts.update_one({'username': session['username']}, {'$set': {'sid': request.sid, 'loggedIn': 'true'}})
        print(f"Updating {session['username']} with socket id {request.sid}")

# Toggle user to offline on socket disconnect
@socketio.on('disconnect')
def disconnect():
    print("Disconnecting session")
    if 'username' in session:
        accounts.update_one({'username': session['username']}, {'$set': {'loggedIn': 'false'}})


# Receive direct message and send to user
@socketio.on('send_msg')
def send_msg(json_data):
    data = json.loads(json_data)
    from_user = accounts.find_one({'sid': request.sid})
    send_data = json.dumps({'sender': from_user['username'], 'msg': data['msg']})
    to_user = accounts.find_one({'username': data['username']})
    print(to_user['loggedIn'])
    if to_user['loggedIn'] != 'false':
        emit("receive_msg", send_data, to=to_user['sid'])
    else:
        send_data = json.dumps({'sender': "Server", 'msg': data['username'] + " is offline or in settings, please refresh page."})
        emit("receive_msg", send_data, to=request.sid)


@socketio.on('my event')
def handle_message(data):
    global votes
    global id 

    # Setting a unique ID for each message to be accessed by the vote
    id = id + 1
    votes[id] = 0 
    data['votes'] = votes[id]
    data['id'] = id 
    

    emit('my response', data , broadcast=True)

@socketio.on('vote')
def handle_event(div_id):
    global votes  

    # votes[id] isnt set here yet?
    votes[div_id] = votes[div_id] + 1

    emit('vote_update', {
        'votes':votes[div_id], 
        'div_id':div_id
    }, broadcast=True) 
# TODO: Dict with id and then amount of votes since the id is specific to each message    

if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", "8000", debug=True)