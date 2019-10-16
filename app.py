from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
""" Below we are setting up our MongoDB Client"""
client = MongoClient()
db = client.WIFIOUTLET
users = db.users
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def log_page():
    """ Renders LoginPage, First PAGE
        That Users will encounter"""
    print("Entering loging page", users.find())
    error = request.form.get('error')
    if error is not None:
        return render_template('login_page.html', error=error)
    else:
        return render_template('login_page.html')


@app.route('/home_page', methods=['POST'])
def home_page():
    """ If account exists in the database
        We will render the homepage"""
    user = users.find_one({'username': request.form.get('username')},
                          {'password': request.form.get('password')})
    user_2 = users.find_one({'email': request.form.get('username')},
                          {'password': request.form.get('password')})
    if user is not None or user_2 is not None:
        if user is None:
            print("By Email", user_2)
            return render_template('user_home_page.html', user=users.find_one({'_id': ObjectId(user_2['_id'])}))
        else:
            print("By Username", user)
            return render_template('user_home_page.html', user=users.find_one({'_id': ObjectId(user['_id'])}))
    else:  # Change the URL later, use url_for rather then rendering template
        return render_template('login_page.html', error=True)


@app.route('/create_user', methods=['GET'])
def create_user():
    return render_template('create_page.html')


@app.route('/creation_verify', methods=['POST'])
def account_verify():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    phone_number = request.form.get('phone_number')
    desire_user = {
            'username': username,
            'password': password,
            'email': email,
            'name': name,
            'lastname': lastname,
            'phone_number': phone_number,
            'Sections': []
    }
    user = users.find_one({'username': request.form.get('username')})
    user_2 = users.find_one({'email': request.form.get('email')})

    if user is None and user_2 is None and username != "" and password != "" and email != "" and name != "" and lastname != "" and phone_number != "":
        users.insert_one(desire_user)
        return redirect(url_for('log_page'))
    else:
        for user in users.find():
            print(user)
        return render_template('create_page.html', error=True)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
