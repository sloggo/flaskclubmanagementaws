import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import jinja2
from flask_login import current_user
import app

def createClub():
    ownerID = request.form['coordinatorID']
    name = request.form['clubName']
    desc = request.form['clubDesc']

    # check if club exists under coordinator
    conn = db.connect(app.local_db_file)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Clubs WHERE CoordinatorID = ?', (ownerID,))
    existsClub = cursor.fetchone()

    if not existsClub:
        cursor.execute('INSERT INTO Clubs (Name, Description, CoordinatorID, ValidityStatus) VALUES (?,?,?, \'Valid\')',
                       (name, desc, ownerID,))
        cursor.execute('SELECT clubID FROM Clubs WHERE CoordinatorID = ?', (ownerID,))
        clubID = cursor.fetchone()[0]
        cursor.execute('INSERT INTO ClubMemberships (UserID, ClubID, RequestStatus) VALUES (?,?, \'Approved\')',
                       (ownerID, clubID))
        conn.commit()

    return redirect(url_for('myclub'))

def joinClub():
    # check if user is a member of the club already
    clubid = request.form['club']
    conn = db.connect(app.local_db_file)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ClubMemberships WHERE UserID = ?', (current_user.id,))
    all_memberships = cursor.fetchall()
    if len(all_memberships) >= 3:
        flash('Unable to join, there is a limit of 3 club memberships per user', 'error')
        return redirect(url_for('clubpage', id=clubid))
    cursor.execute('SELECT * FROM ClubMemberships WHERE UserID = ? AND ClubID = ?', (current_user.id, clubid))
    exists = cursor.fetchone()
    if exists:
        flash('Unable to join, you are already a member!', 'error')
        return redirect(url_for('clubpage', id=clubid))
    else:
        cursor.execute('INSERT INTO ClubMemberships (UserID,ClubID ) VALUES (?, ?)', (current_user.id, clubid))
        conn.commit()
    return redirect(url_for('profile'))

def clubpage(id):
    conn = db.connect(app.local_db_file)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Clubs WHERE clubid = ?', (id,))
    club_data = cursor.fetchone()

    cursor.execute('SELECT * FROM Users WHERE userid = ?', (club_data[4],))
    owner_data = cursor.fetchone()
    return render_template('clubpage.html', club_data=club_data, owner_data=owner_data)

def explore():
    conn = db.connect(app.local_db_file)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Clubs')
    club_data = cursor.fetchall()
    return render_template('/explore.html', club_data=club_data)