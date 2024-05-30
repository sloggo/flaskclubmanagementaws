import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import jinja2
from flask_login import current_user
def contact():
    return render_template('/contact.html')
def about():
    return render_template('/about.html')
def home():
    return render_template('/home.html')
def login():
    return render_template('/login.html')
def register():
    return render_template('/register.html')
def events():
    return render_template('/events.html')
