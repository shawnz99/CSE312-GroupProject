from flask import Flask, render_template, request
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['C3WAT']
accounts = db['accounts']

@app.route('/')
def home():
    return render_template('index.html')

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
    app.run(debug=True)