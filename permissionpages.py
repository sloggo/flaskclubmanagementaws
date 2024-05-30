import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import jinja2
from flask_login import current_user
import app
def myclub():
    if current_user is None:
        return render_template('/home.html',)
    else:
        conn = db.connect(app.local_db_file)

        cursor = conn.cursor()
        # fetch role of current user
        conn = db.connect(app.local_db_file)

        cursor = conn.cursor()
        cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
        role_data = cursor.fetchone()

        cursor.execute('SELECT * FROM Clubs WHERE CoordinatorID = ?', (current_user.id,))
        club_owner = cursor.fetchone()

        if role_data[0] == 'Coordinator' and club_owner:
            cursor.execute('''
                        SELECT u.UserID, u.Username, u.Contact, u.Email, c.RequestStatus, c.CreatedAt
                        FROM Users u 
                        JOIN ClubMemberships c ON u.UserID = c.UserID 
                        WHERE c.ClubID = ?
                    ''', (club_owner[0],))
            club_users = cursor.fetchall()

            cursor.execute('''
                SELECT * from Events WHERE ClubID = ?
            ''', (club_owner[0],))
            event_data = cursor.fetchall()
            registered_data = []

            for event in event_data:
                cursor.execute('''
                                SELECT Users.UserID, Users.Username, Users.Contact, Users.Email, EventRegistrations.Status
                                FROM Users
                                JOIN EventRegistrations ON Users.UserID = EventRegistrations.UserID
                                WHERE EventRegistrations.EventID = ?
                            ''', (event[0],))
                registered_data.append(cursor.fetchall())

            print(registered_data)

            return render_template('/myclubmanage.html', current_user=current_user, club_data=club_owner, club_users=club_users, event_data=event_data, registered_data=registered_data)
        elif role_data[0] == 'Coordinator' and club_owner is None:
            return render_template('/myclubcreate.html', current_user=current_user)

def admin():
    if current_user is None:
        return render_template('/home.html',)
    else:
        # fetch role of current user
        conn = db.connect(app.local_db_file)

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
        role_data = cursor.fetchone()
        # fetch users data
        cursor.execute('SELECT userid, username, email, contact, role, CreatedAt,approvalstatus FROM Users WHERE Role != \'Admin\'')
        user_data = cursor.fetchall()

        return render_template('/admin.html', current_user=current_user, role=role_data[5], users_data=user_data)