from flask import request, render_template, redirect, url_for, session
import re
from flask_app import app, db, cursor


# define a route
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM rando_project_login WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result If account exists in rando_project_login table in our database
        account = cursor.fetchone()
        # Creates a session, able to adventure around the site as it makes the account active
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('homepage'))
        else:
            # Account doesn't exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login_page.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM rando_project_login WHERE username = %s OR email = %s', (username, email))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exist with email or account name!'
            # re.match () is used to match a regular expression to the beginning of a string
            # re.match(pattern, string)
            # Pattern - pattern is the regular expression pattern to be matched
            # String - string is the string to be searched for a match
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesn't exist and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO rando_project_login VALUES (NULL, %s, %s, %s)', (username, password, email,))
            db.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registration.html', msg=msg)


@app.route('/homepage')
def homepage():
    # Checked if the user is logged in
    if 'loggedin' in session:
        # user is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user, so we can display it on the profile page
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM rando_project_login WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/music_chart')
def music_chart():
    if 'loggedin' in session:
        # execute a query
        cursor.execute("SELECT * FROM rando_project ORDER BY timestamp_formatted DESC;")

        # fetch all rows
        data = cursor.fetchall()

        # pass the data to the template
        return render_template('music_chart.html', data=data)
    return redirect(url_for('profile'))


@app.route('/Dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():  # ATTEMPT PUT METHOD WHEN HAVE THE CHANCE
    # Check if user is logged in
    if 'loggedin' not in session:
        # If not logged in, redirects to login page
        return redirect(url_for('login'))
    # Fetch log in information from database
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM rando_project_login WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    # Handle form submission
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Fetch to assure username or email is not taken
        cursor.execute('SELECT * FROM rando_project_login WHERE email = %s AND id != %s', (email, session['id'],))
        existing_email = cursor.fetchone()
        # Check if username is already in the database
        cursor.execute('SELECT * FROM rando_project_login WHERE username = %s AND id != %s', (username, session['id'],))
        existing_username = cursor.fetchone()
        # If form username and form email is the same as the username and email logged in, no changes has been made
        if username == account['username'] and email == account['email']:
            no_change_msg = 'No changes has been made.'
            return render_template('edit_profile.html', account=account, user_msg=no_change_msg)
        # If email and username do not exist in the database but password is incorrect, no changes occurs
        elif not existing_email and not existing_username and not account['password']:
            wrong_pw_msg = 'Incorrect password.'
            return render_template('edit_profile.html', account=account, wrong_pw_msg=wrong_pw_msg)
        # If email and username do not exist in the db and pw is correct
        elif not existing_email and not existing_username and account['password']:
            # Update the user's email and username
            cursor.execute('UPDATE rando_project_login SET email = %s, username = %s WHERE id = %s',
                           (email, username, session['id'],))
            db.commit()
            return redirect(url_for('profile'))
        elif existing_email:
            # Email is already in the database
            email_msg = 'Email is already in use.'
            return render_template('edit_profile.html', account=account, email_msg=email_msg)
        elif existing_username:
            # Username is already in the database
            user_msg = 'Username is already in use.'
            return render_template('edit_profile.html', account=account, user_msg=user_msg)
        else:
            # Both email and username are None, this should not happen
            error_msg = 'An error occurred. Please try again.'
            return render_template('edit_profile.html', account=account, error_msg=error_msg)
    # If user is logged, go to the edit profile page
    return render_template('edit_profile.html', account=account)


@app.route('/change_password', methods=['POST', 'GET'])
def change_password():  # ATTEMPT PUT METHOD WHEN HAVE THE CHANCE
    # Check if user is logged in
    if 'loggedin' not in session:
        # If not logged in, redirects to login page
        return redirect(url_for('login'))
    # Fetch log in information from database
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM rando_project_login WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    # Handle form submission
    if request.method == 'POST' and 'current_password' in request.form and 'new_password' in request.form:
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        # If new password is the same password as the user logged in, no change occurs
        if new_password == account['password']:
            existing_pw_msg = "You're currently using this password"
            return render_template('change_password.html', account=account, existing_pw_msg=existing_pw_msg)
        # If new password is not the same as current password but current input password is not the same as current
        # existing password, no changes occur
        elif new_password != account['password'] and current_password != account['password']:
            incorrect_pw_msg = 'Incorrect password'
            return render_template('change_password.html', account=account, incorrect_pw_msg=incorrect_pw_msg)
        # if new password not the same as current and current pw input same as current password set, changes it
        elif new_password != account['password'] and current_password == account['password']:
            cursor.execute('UPDATE rando_project_login SET password = %s WHERE id = %s', (new_password, session['id'],))
            db.commit()
            success_mg = 'Password successfully changed.'
            return render_template('change_password.html', account=account, success_mg=success_mg)
    return render_template('change_password.html', account=account)
