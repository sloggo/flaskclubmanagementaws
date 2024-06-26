
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3 as db
import json
import boto3
# flask --app app.py --debug run
import hashlib
import auth
import clubs
import events
import static
import updates, permissionpages
import os


class ClientError:
    pass
import boto3
from botocore.exceptions import ClientError
from flask import Flask

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def get_secret():
    secret_name = "db_key"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        json_string = get_secret_value_response['SecretString']
        data = json.loads(json_string)
        return data.get('SECRET_KEY')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnrecognizedClientException':
            print("UnrecognizedClientException: The security token included in the request is invalid.")
        else:
            print(f"ClientError: {e}")
        raise e

app.config['SECRET_KEY'] = get_secret()
s3 = boto3.client('s3')

def download_db_from_s3(bucket_name, file_key, local_file_path):
    s3.download_file(bucket_name, file_key, local_file_path)

# Fetch SQLite database file from S3
bucket_name = 'cloudcook'
file_key = 'user_data.db'
local_db_file = '/tmp/database.db'  # Local path to save the downloaded file
download_db_from_s3(bucket_name, file_key, local_db_file)

def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    s32 = boto3.resource('s3')
    bucket = s32.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

download_s3_folder(bucket_name, "images", "./static/images")


# Permission based pages
app.add_url_rule('/myclub', view_func=permissionpages.myclub)
app.add_url_rule('/admin', view_func=permissionpages.admin)


# Update queries
app.add_url_rule('/updateClubMember', methods=['GET', 'POST'], view_func=updates.updateClubMember)
app.add_url_rule('/updateMember', methods=['GET', 'POST'], view_func=updates.updateMember)

# Club based pages
app.add_url_rule('/joinClub', methods=['GET', 'POST'], view_func=clubs.joinClub)
app.add_url_rule('/createClub', methods=['GET', 'POST'], view_func=clubs.createClub)
app.add_url_rule('/explore/<int:id>', view_func=clubs.clubpage)
app.add_url_rule('/explore', view_func=clubs.explore)
app.add_url_rule("/events", view_func=events.eventsPage)
app.add_url_rule("/createEvent", methods=['GET', 'POST'], view_func=events.createEvent)
app.add_url_rule("/joinEvent", methods=['GET', 'POST'], view_func=events.joinEvent)

# Static pages
app.add_url_rule('/', view_func=static.home)
app.add_url_rule('/home', view_func=static.home)
app.add_url_rule('/contact', view_func=static.contact)
app.add_url_rule('/about', view_func=static.about)
app.add_url_rule('/login', view_func=static.login)
app.add_url_rule('/register', view_func=static.register)
app.add_url_rule('/events', view_func=static.events)

# Authentication
app.add_url_rule("/profile", view_func=auth.profile)
app.add_url_rule("/logout", view_func=auth.logout)
app.add_url_rule("/retrieveData/<int:id>", methods=['GET', 'POST'], view_func=auth.retrieve_user_data)
app.add_url_rule("/registerProcess", methods=['POST'], view_func=auth.registerDataProcess)
app.add_url_rule("/loginProcess", methods=['GET', 'POST'], view_func=auth.loginDataProcess)

@login_manager.user_loader
def load_user(user_id):
    conn = db.connect(local_db_file)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return auth.User(user_data[0], user_data[1])

@app.context_processor
def utility_processor():
    def current_user_data():
        if current_user.is_authenticated:
            conn = db.connect(local_db_file)

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
            currentUsrData = cursor.fetchone()
            cursor.close()
            conn.close()
            clubname = None
            if currentUsrData[5] == "Coordinator":
                conn = db.connect(local_db_file)

                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Clubs WHERE CoordinatorID=?',(current_user.id,))
                club = cursor.fetchone()
                clubname = ""
                if club:
                    clubname = club[1]
            print(clubname)
            userData = auth.USERDATA(
                currentUsrData[1],
                currentUsrData[3],
                currentUsrData[4],
                currentUsrData[5],
                currentUsrData[6],
                clubname
            )
            return userData
        return auth.USERDATA(
            None,
            None,
            None,
            None,
            None,
            None
        )

    return dict(user_data=current_user_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)