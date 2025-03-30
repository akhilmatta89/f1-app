import os

import firebase_admin
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from firebase_admin import credentials, firestore, auth
from firebase_admin import credentials, firestore
from functools import wraps
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'


# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    # Check if the user is logged in
    if 'user' not in session:
        return render_template('home.html')

    # Fetch all drivers from Firestore
    drivers_ref = db.collection('drivers').stream()
    drivers = []

    for doc in drivers_ref:
        driver_data = doc.to_dict()
        driver_data['id'] = doc.id  # Add the document ID to the driver data
        drivers.append(driver_data)

    # Render the home template with the list of drivers
    return render_template('home.html', drivers=drivers)

# About Page Route
@app.route("/about")
def about():
    return render_template("about.html", logged_in=("user" in session))


########################################
""" Authentication and Authorization """


# Decorator for routes that require authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return redirect(url_for('login'))

        else:
            return f(*args, **kwargs)

    return decorated_function

@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401

    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        session['user'] = decoded_token  # Add user to session
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", session)  # Validate token here
        return redirect(url_for('dashboard'))

    except:
        print("####################################")
        return "Unauthorized", 401

# Route to set session after login
@app.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    session['user'] = data['uid']  # Store user UID in session
    return jsonify({'status': 'success'})

# Route to clear session after logout
@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.pop('user', None)  # Clear user session
    return jsonify({'status': 'success'})

@app.route('/dashboard')
@auth_required
def dashboard():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # Optionally clear the session cookie
    return response

@app.route('/add_driver_page', methods=['GET', 'POST'])
def add_driver_page():
    return render_template('add_driver.html')

@app.route('/update_driver_page', methods=['GET', 'POST'])
def update_driver_page():
    return render_template('update_driver.html')

@app.route('/compare_drivers_page', methods=['GET', 'POST'])
def compare_drivers_page():
    return render_template('compare_drivers.html')

@app.route('/add_driver', methods=['GET', 'POST'])
def add_driver():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', 'Unknown')
        age = int(request.form.get('age', 0))  # Default to 0 if not provided
        team = request.form.get('team', 'Unknown')
        pole_positions = int(request.form.get('pole_positions', 0))
        race_wins = int(request.form.get('race_wins', 0))
        points_scored = int(request.form.get('points_scored', 0))
        total_world_titles = int(request.form.get('total_world_titles', 0))
        total_fastest_laps = int(request.form.get('total_fastest_laps', 0))

        db.collection('drivers').add({
            "name": name,
            "age": age,
            "team": team,
            "total_pole_positions": pole_positions,
            "total_race_wins": race_wins,
            "total_points_scored": points_scored,
            "total_world_titles": total_world_titles,
            "total_fastest_laps": total_fastest_laps
        })

        return redirect(url_for('home'))

    return render_template('add_driver.html')


@app.route('/query_driver', methods=['GET', 'POST'])
def query_driver():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    if request.method == 'POST':
        attribute = request.form['attribute']
        condition = request.form['condition']
        value = int(request.form['value'])

        drivers_ref = db.collection('drivers')
        if condition == "greater_than":
            query = drivers_ref.where(attribute, ">", value).stream()
        elif condition == "less_than":
            query = drivers_ref.where(attribute, "<", value).stream()
        else:
            query = drivers_ref.where(attribute, "==", value).stream()

        drivers = [doc.to_dict() for doc in query]
        return render_template('query_driver.html', drivers=drivers)

    return render_template('query_driver.html', drivers=[])


@app.route('/edit_driver/<driver_id>', methods=['POST'])
def edit_driver(driver_id):
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get the driver document from Firestore
    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()

    # Check if the driver exists
    if not driver.exists:
        return render_template('update_driver.html', error="Driver not found. Please check the Driver ID.")

    # Update the driver's data with the form submission
    updated_data = {
        "name": request.form['name'],
        "age": int(request.form['age']),
        "team": request.form['team'],
        "total_pole_positions": int(request.form.get('total_pole_positions', 0)),
        "total_race_wins": int(request.form.get('total_race_wins', 0)),
        "total_points_scored": int(request.form.get('total_points_scored', 0)),
        "total_world_titles": int(request.form.get('total_world_titles', 0)),
        "total_fastest_laps": int(request.form.get('total_fastest_laps', 0))
    }

    # Update the driver document in Firestore
    driver_ref.update(updated_data)

    # Redirect to the home page after updating
    return redirect(url_for('home'))

@app.route('/update_driver', methods=['GET'])
def update_driver():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get the Driver ID from the query parameters
    driver_id = request.args.get('driver_id')

    # If no Driver ID is provided, render the update_driver.html template without driver data
    if not driver_id:
        return render_template('update_driver.html')

    # Fetch the driver from Firestore
    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()

    # Check if the driver exists
    if not driver.exists:
        return render_template('update_driver.html', error="Driver not found. Please check the Driver ID.")

    # Convert Firestore document to a dictionary
    driver_data = driver.to_dict()
    driver_data['id'] = driver_id  # Add the document ID to the driver data

    # Render the update_driver.html template with the driver's data
    return render_template('update_driver.html', driver=driver_data)

@app.route('/compare_drivers', methods=['GET', 'POST'])
def compare_drivers():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    if request.method == 'POST':
        # Get driver IDs from the form
        driver1_id = request.form['driver1_id']
        driver2_id = request.form['driver2_id']

        # Fetch driver data from Firestore
        driver1 = db.collection('drivers').document(driver1_id).get()
        driver2 = db.collection('drivers').document(driver2_id).get()

        # Check if both drivers exist
        if driver1.exists and driver2.exists:
            driver1_data = driver1.to_dict()
            driver2_data = driver2.to_dict()
            return render_template('compare_drivers.html', driver1=driver1_data, driver2=driver2_data)
        else:
            error = "One or both drivers not found. Please check the IDs and try again."
            return render_template('compare_drivers.html', error=error)

    # If it's a GET request, render the compare_drivers.html template
    return render_template('compare_drivers.html')

@app.route('/get_driver', methods=['GET', 'POST'])
def get_drivers_data():
    # Check if the user is logged in
    # if 'user' not in session:
    #     return redirect(url_for('login'))  # Redirect to login if not logged in
    global driver_id
    if request.method == "POST":
        driver_id = request.form['driver_id']
        driver_data= db.collection('drivers').document(driver_id).get()
        return render_template('get_driver.html', driver=driver_data.to_dict())

    return render_template('get_driver.html')






if __name__ == "__main__":
    app.run()

