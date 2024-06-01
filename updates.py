import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import jinja2
from flask_login import current_user


def updateClubMember():
    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()

    cursor.execute('SELECT CoordinatorID FROM Clubs WHERE ClubID = ?', (int(request.form['clubID']),))
    club_owner_id = cursor.fetchone()
    print(current_user.id, club_owner_id)
    if user_data[0] == "Coordinator" and current_user.id == club_owner_id[0]:
        approved = ''
        if request.form['approval'] is not None and request.form['approval'] == 'on':
            approved = 'Approved'
            cursor.execute('UPDATE ClubMemberships SET RequestStatus = ? WHERE UserID = ? AND ClubID = ?',
                           (approved, int(request.form['userID']), int(request.form['clubID'])))
            conn.commit()

        return redirect(url_for('myclub'))
    else:
        return redirect(url_for('home'))

def updateMember():
    conn = db.connect('/tmp/database.db')

    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    if user_data[0] == "Admin":
        print(request.form['userID'], request.form['role'])

        approved = ''
        if request.form['approval'] is not None and request.form['approval'] == 'on':
            approved = 'Approved'
            cursor.execute('UPDATE Users SET Role = ?, ApprovalStatus = ? WHERE UserID = ?',
                           (request.form['role'], approved, int(request.form['userID'])))
            conn.commit()
        else:
            cursor.execute('UPDATE Users SET Role = ? WHERE UserID = ?',
                           (request.form['role'], int(request.form['userID'])))
            conn.commit()

        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))


