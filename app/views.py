# app/views.py

from flask import render_template

from app import app

@app.route('/')
def index():
    return render_template('index.html')

# Add routes for login, register, dashboard, etc.
