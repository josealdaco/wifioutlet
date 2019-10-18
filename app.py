from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
""" Below we are setting up our MongoDB Client"""
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/WIFIOUTLET')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
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


@app.route('/user_settings', methods=['POST'])
def user_settings():
    """ Recieved user data and renders settings page"""
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    section_len = len(user['Sections'])
    return render_template('user_settings.html', user=user, section_len=section_len)


@app.route('/delete/account', methods=['POST'])
def delete_account():
    user = request.form.get('user')
    print("This is the user that wants to be removed:", user)
    db.users.remove({'_id': ObjectId(request.form.get('user'))})
    return redirect(url_for('log_page'))


@app.route('/home_page', methods=['POST'])
def home_page():
    """ If account exists in the database
        We will render the homepage"""
    user = users.find_one({'username': request.form.get('username'),
                          'password': request.form.get('password')})
    user_2 = users.find_one({'email': request.form.get('username'),
                          'password': request.form.get('password')})

    # If we are returing to the webpage
    if user is not None or user_2 is not None:
        if user is None:
            user_2 = users.find_one({'_id': ObjectId(user_2['_id'])})
            print("By Email", user_2)
            section_len = len(user_2['Sections'])
            if section_len != 0:
                sum = 0
                for device in range(len(user_2['Sections'])):
                    for port in range(len(user_2['Sections'][device]['devices'])):
                        sum += int(user_2['Sections'][device]['devices'][port]['device']['port_number']) * int(user_2['Sections'][device]['devices'][port]['port0']['power'])
            return render_template('user_home_page.html', user=user_2, section_len=section_len, total_consumption=sum, total_cost=sum*.4)
        else:
            user = users.find_one({'_id': ObjectId(user['_id'])})
            print("By Username", user)
            section_len = len(user['Sections'])
            sum = 0
            if section_len != 0:
                for device in range(len(user['Sections'])):
                    for port in range(len(user['Sections'][device]['devices'])):
                        sum += int(user['Sections'][device]['devices'][port]['device']['port_number']) * int(user['Sections'][device]['devices'][port]['port0']['power'])
            return render_template('user_home_page.html', user=user, section_len=section_len, total_consumption=sum, total_cost=sum*.4)
    else:  # Change the URL later, use url_for rather then rendering template
        return render_template('login_page.html', error=True)


@app.route('/profile/update', methods=['POST'])
def update_profile():
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    phone_number = request.form.get('phone_number')

    return render_template('update_profile.html', username=username, email=email, password=password, name=name, lastname=lastname, phone_number=phone_number, user=user)


@app.route('/user_home_page', methods=['POST'])  # Will render the home page for the user
def user_home_page():
    """ Renders home page for user"""
    user_id = request.form.get('user')
    user = users.find_one({'_id': ObjectId(user_id)})
    section_len = len(user['Sections'])
    sum = 0
    if section_len != 0:
        for device in range(len(user['Sections'])):
            for port in range(len(user['Sections'][device]['devices'])):
                #print("This is the devices in section 1:", user['Sections'][device]['devices'][0]['port0'])
                sum += int(user['Sections'][device]['devices'][port]['device']['port_number']) * int(user['Sections'][device]['devices'][port]['port0']['power'])
    return render_template('user_home_page.html', user=user, section_len=section_len, total_consumption=sum, total_cost=sum*.4)


@app.route('/add/devices', methods=['POST'])
def add_devices():
    """This is where we render the add device template"""
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    print("user in adding devices:", user)
    return render_template('device_form.html', user=user)


@app.route('/publish/devices', methods=['POST'])
def publish_devices():
    """ Adding devices to account"""
    device_name = request.form.get('device_name')
    port_number = int(request.form.get('port_number'))
    power_consumption = float(request.form.get('power_consumption'))
    section_name = request.form.get('section_name')
    device_number = int(request.form.get('device_number'))
    section_image = request.form.get('section_image')
    section_image2 = request.form.get('section_image2')
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    print("This is first section:", section_image)
    print("This is second section:", section_image2)
    if section_image == "":
        print("we will insert computer image here")
        section = {
                'name': section_name,
                'devices': [],
                'image': section_image2
                }
    else:
        section = {
                'name': section_name,
                'devices': [],
                'image': section_image
                }

        #  Input device with name and port amount
    for index in range(device_number):
        section['devices'].append(({'device': {
                            'name': device_name,
                            'port_number': port_number,
                            }}))
    # Input port and each of their consumption
    print("This is the length of dict:", len(section))
    for value in section:
        print("This is the value we are getting:", value)
        if(value == "devices"):
            for total in range(len(section['devices'])):
                for port in range(port_number):
                    print("We are now looping")
                    section['devices'][total].update({'port' + str(port): {'power': power_consumption
                                                                                }})
    # Looping the amount of devices for length
    user2 = users.find_one({'_id': ObjectId(user['_id'])})
    find_index = 0
    for section_2 in range(len(user2['Sections'])):
        print("This is the section we abstract:", user2['Sections'][section_2]['name'])
        if user2['Sections'][section_2]['name'] == section['name']: # Check if the user is trying to append to existing section
            print("We will merge")
            print("lets get the list of devices:", len(section['devices']))
            for current in range(len(section['devices'])):
                user['Sections'][find_index]['devices'].append(section['devices'][current])
            print("This is what we will update:", user['Sections'][find_index]['devices'], len(user['Sections'][find_index]['devices']))
            user['Sections'][find_index].update({'size': len(user['Sections'][find_index]['devices'])})
            user_update = {
                    'username': user['username'],
                    'password': user['password'],
                    'email': user['email'],
                    'name': user['name'],
                    'lastname': user['lastname'],
                    'phone_number': user['phone_number'],
                    'Sections': user['Sections']
            }

            users.update_one({'_id': ObjectId(user['_id'])},
                            {'$set': user_update})
            return render_template('outlet_page.html', user=user)
        find_index += 1

    section.update({'size': len(section['devices'])})
    user['Sections'].append(section)
    # Update the user with the new section
    user_update = {
            'username': user['username'],
            'password': user['password'],
            'email': user['email'],
            'name': user['name'],
            'lastname': user['lastname'],
            'phone_number': user['phone_number'],
            'Sections': user['Sections']
    }

    users.update_one({'_id': ObjectId(user['_id'])},
                    {'$set': user_update})




    print("This is the new user with a section:", user)
    return render_template('outlet_page.html', user=user)


@app.route('/money_page', methods=['POST'])  # Will render the money page for user
def momey_page():
    """ Renders money page for user"""
    user_id = request.form.get('user')
    user = users.find_one({'_id': ObjectId(user_id)})
    section_len = len(user['Sections'])
    return render_template('money_page.html', user=user, section_len=section_len)


@app.route('/outlet_page', methods=['POST'])  # Will render the outlet page for user
def outlet_page():
    user_id = request.form.get('user')
    user = users.find_one({'_id': ObjectId(user_id)})
    """ Renders outlet page for user"""
    section_len = len(user['Sections'])
    return render_template('outlet_page.html', user=user, section_len=section_len)


@app.route('/create_user', methods=['GET'])
def create_user():
    """ Directs user to create user page"""
    return render_template('create_page.html')


@app.route('/user_profile', methods=['POST'])
def user_profile():
    """ Gets user data and renders the page"""
    if request.method == 'POST':
        user_id = request.form.get('user')
        print("This is what we get:", user_id)
        user = users.find_one({'_id': ObjectId(user_id)})
        return render_template('user_profile.html', user=user, section_len=len(user['Sections']))


@app.route('/publish/profile', methods=['POST'])
def publish_profile():
    """ Returns user to the User info section"""
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    phone_number = request.form.get('phone_number')
    # IF statements check if the user did not make a change
    if username == "":
        username = user['username']
    if email == "":
        print("The email was left blank!")
        email = user['email']
    if password == "":
        password = user['password']
    if name == "":
        name = user['name']
    if lastname == "":
        lastname = user['lastname']
    if phone_number == "":
        phone_number = user['phone_number']

    profile_update = {
        'username': username,
        'email': email,
        'password': password,
        'name': name,
        'lastname': lastname,
        'phone_number': phone_number,
        'Sections': user['Sections']
    }
    users.update_one({'_id': ObjectId(user['_id'])},
                    {'$set': profile_update})

    print("New updated profile:", user)
    return render_template('user_profile.html', user=users.find_one({'_id': ObjectId(user['_id'])}), section_len=len(user['Sections']))


@app.route('/user/section', methods=['POST'])
def user_section():
    """ View section and control devices"""
    user = users.find_one({'_id': ObjectId(request.form.get('user'))})
    section_name = request.form.get('section')  # Current section selected
    index = 0
    for data in user['Sections']:
        if data['name'] == section_name:
            break
        index += 1
    section = user['Sections'][index]  # We search for the correct data
    return render_template('section_form.html', user=user, section=section)


@app.route('/creation_verify', methods=['POST'])
def account_verify():
    """ Verifies if the account being created already exists"""
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
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
