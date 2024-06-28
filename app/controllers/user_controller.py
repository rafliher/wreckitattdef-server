# user_controller.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.models import User
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/api/user', methods=['GET'])
@jwt_required()
def api_user():
    users = User.query.filter(User.is_admin == False).all()

    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

@app.route('/user', methods=['GET'])
@login_required
def user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.filter(User.is_admin == False).all()
    return render_template('user_management.html', users=users)

@app.route('/user', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    host_ip = request.form.get('host_ip')
    
    user = User(username=username, password_hash=generate_password_hash(password), host_ip=host_ip)
    db.session.add(user)
    db.session.commit()
    
    flash('User added successfully!', 'success')
    return 'User added successfully!'

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return 'User deleted successfully!'

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    username = request.form.get('username')
    host_ip = request.form.get('host_ip')
    password = request.form.get('password')

    if username:
        user.username = username
    if host_ip:
        user.host_ip = host_ip
    if password:
        user.password_hash = generate_password_hash(password)

    db.session.commit()
    
    flash('User updated successfully!', 'success')
    return 'User updated successfully!'

import json

@app.route('/user/import', methods=['POST'])
@login_required
def import_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('user'))

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.json'):
        flash('Invalid file format! Please upload a JSON file.', 'error')
        return redirect(url_for('user'))

    try:
        json_data = json.load(file)
    except Exception as e:
        flash('Error reading JSON file: {}'.format(str(e)), 'error')
        return redirect(url_for('user'))

    print(json_data)

    if not isinstance(json_data, list):
        flash('Invalid JSON format! Please provide a list of user objects.', 'error')
        return redirect(url_for('user'))

    for user_data in json_data:
        if not isinstance(user_data, dict):
            flash('Invalid user data format! Skipping user because not a dict: ' + user_data, 'warning')
            continue

        username = user_data.get('username')
        password_hash = user_data.get('password_hash')
        host_ip = user_data.get('host_ip')

        if not all([username, password_hash, host_ip]):
            flash('Incomplete user data! Skipping user because invalid format: ' + user_data, 'warning')
            continue

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User "{}" already exists! Skipping user.'.format(username), 'warning')
            continue

        new_user = User(username=username, password_hash=password_hash, host_ip=host_ip)
        db.session.add(new_user)

    db.session.commit()

    flash('Users imported successfully!', 'success')
    return redirect(url_for('user'))

@app.route('/user/export', methods=['GET'])
@login_required
def export_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.filter(User.is_admin == False).all()
    user_data = [{'username': user.username, 'password_hash': user.password_hash ,'host_ip': user.host_ip} for user in users]
    
    # Convert user data to JSON format
    json_data = json.dumps(user_data, indent=4)
    
    # Set response headers for file download
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=users.json'}
    )
    
    return response