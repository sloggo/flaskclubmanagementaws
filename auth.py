from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import hashlib

def calculate_sha256(input_data):
    sha256_hash = hashlib.sha256(input_data.encode()).hexdigest()
    return sha256_hash

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

def loginDataProcess():
    username = request.form.get('loginName')
    password = request.form.get('loginPassword')
    hashedPass = calculate_sha256(password)
    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', (username, hashedPass))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        user = User(user_data[0], user_data[1])
        login_user(user)
        return redirect(url_for('profile'))
    else:
        flash('Incorrect username or password. Please try again.', 'error')
    return redirect(url_for('login'))


def registerDataProcess():
    username = request.form.get('Username')
    password = request.form.get('Password')
    hashedPass = calculate_sha256(password)
    email = request.form.get('Email')
    contact = request.form.get('mobileNumber')
    print(username, password, hashedPass, email, contact)

    password_repeat = request.form.get('RepeatPassword')

    if not username or not password or not password_repeat or password != password_repeat:
        flash('Invalid registration data. Please check your inputs.', 'error')
        return redirect(url_for('register'))

    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()

    cursor.execute('SELECT Username FROM Users WHERE Username = ?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        flash('Username already exists. Please choose a different username.', 'error')
        conn.close()
        return redirect(url_for('register'))
    else:
        # Insert the new user into the loginInfo table
        cursor.execute('INSERT INTO Users (Username, Password, Contact, Email, Role) VALUES (?, ?, ?, ?, ?)',
                       (username, hashedPass, contact, email, "Student"))
        conn.commit()

        cursor.execute('SELECT UserID FROM Users WHERE Username = ?', (username,))
        user_id = cursor.fetchone()[0]
        print(type(user_id))
        if user_id == 1:
            cursor.execute('UPDATE Users SET Role = "Admin" WHERE UserID = 1')
            conn.commit()
        conn.close()
        user = User(user_id, username)
        login_user(user)

        return redirect(url_for('profile'))

@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


class USERDATA:
    def __init__(self, username, mobile, email, role, accountStatus, clubname=None) -> None:
        self.username = username
        self.mobile = mobile
        self.email = email
        self.role = role
        self.accountStatus = accountStatus
        self.club = clubname




@login_required
def profile():
    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()
    cursor.execute('SELECT ClubID FROM ClubMemberships WHERE UserID = ?', (current_user.id,))
    clubIDs = cursor.fetchall()
    clubs = []
    cursor.execute('SELECT EventID FROM EventRegistrations WHERE UserID = ?', (current_user.id,))
    eventIDs = cursor.fetchall()
    events = []
    for clubID in clubIDs:
        cursor.execute('SELECT * FROM Clubs WHERE ClubID = ?', clubID)
        club = cursor.fetchone()
        clubs.append(club)
    for eventID in eventIDs:
        cursor.execute('SELECT * FROM Events WHERE EventID = ?', eventID)
        event = cursor.fetchone()
        print(event)
        events.append(event)
    print(clubs, events)
    return render_template('/profile.html', clubs=clubs, events=events)

@login_required
def retrieve_user_data(id):
    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    if user_data[0] == "Admin":
        cursor.execute('SELECT * FROM Users WHERE UserID = ?', (id,))
        user_data = cursor.fetchone()
        return jsonify(user_data)
    else:
        return 'Unauthorised Access'