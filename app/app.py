from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['C3WAT']
accounts = db['accounts']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return "Login"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = {
            'username': request.form['username'],
            'password': request.form['password']
        }

        query = accounts.insert_one(account)
        
        if query.inserted_id:
            msg = 'Account has been created!'
        else:
            msg = 'There was an error creating your account.'
        
        return render_template('register.html', msg=msg)
    else:
        return render_template('register.html')
    
if __name__ == '__main__':
    app.run(debug=True)