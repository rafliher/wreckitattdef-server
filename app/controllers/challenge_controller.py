# challenge_controller.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.models import Challenge,User
from flask_login import login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import requests
import os

load_dotenv()

@app.route('/api/challenges', methods=['GET'])
@jwt_required()
def api_challenges():
    challenges = Challenge.query.all()
    challenges_list = [challenge.serialize() for challenge in challenges]
    return jsonify(challenges_list), 200

@app.route('/api/restart/<string:challenge>', methods=['POST'])
@jwt_required()
def restart_challenge(challenge):
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    url = f'http://{user.host_ip}/restart/{challenge}'

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to restart challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/api/rollback/<string:challenge>', methods=['POST'])
@jwt_required()
def rollback_challenge(challenge):
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    url = f'http://{user.host_ip}/rollback/{challenge}'

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to rollback challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    
@app.route('/api/activate/<string:challenge>', methods=['POST'])
@jwt_required()
def activate_challenge(challenge):
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    url = f'http://{user.host_ip}/activate/{challenge}'

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to activate challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/api/deactivate/<string:challenge>', methods=['POST'])
@jwt_required()
def deactivate_challenge(challenge):
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    url = f'http://{user.host_ip}/deactivate/{challenge}'

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to deactivate challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/api/credential/<string:challenge>', methods=['POST'])
@jwt_required()
def challenge_credential(challenge):
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    url = f'http://{user.host_ip}/credential/{challenge}'

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to fetch challenge credential.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/challenges', methods=['GET'])
@login_required
def challenges():
    challenges = Challenge.query.all()
    return render_template('challenge_management.html', challenges=challenges)

@app.route('/challenge', methods=['POST'])
@login_required
def add_challenge():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    name = request.form.get('name')
    title = request.form.get('title')
    port = request.form.get('port')
    description = request.form.get('description')
    
    challenge = Challenge(name=name, title=title, port=port, description=description)
    db.session.add(challenge)
    db.session.commit()
    
    flash('Challenge added successfully!', 'success')
    return 'Challenge added successfully!'

@app.route('/challenge/<int:challenge_id>', methods=['DELETE'])
@login_required
def delete_challenge(challenge_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    
    return 'Challenge deleted successfully!'

@app.route('/challenge/<int:challenge_id>', methods=['PUT'])
@login_required
def edit_challenge(challenge_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    challenge.title = request.form.get('title')
    challenge.port = request.form.get('port')
    challenge.description = request.form.get('description')

    db.session.commit()
    
    flash('Challenge updated successfully!', 'success')
    return 'Challenge updated successfully!'

import json


@app.route('/challenge/import', methods=['POST'])
@login_required
def import_challenges():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('challenges'))

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.json'):
        flash('Invalid file format! Please upload a JSON file.', 'error')
        return redirect(url_for('challenges'))

    try:
        json_data = json.load(file)
    except Exception as e:
        flash('Error reading JSON file: {}'.format(str(e)), 'error')
        return redirect(url_for('challenges'))

    print(json_data)

    if not isinstance(json_data, list):
        flash('Invalid JSON format! Please provide a list of user objects.', 'error')
        return redirect(url_for('challenges'))

    for challenge_data in json_data:
        if not isinstance(challenge_data, dict):
            flash(f'Invalid challenge data format! Skipping user because not a dict: {challenge_data}', 'warning')
            continue

        title = challenge_data.get('title')
        port = challenge_data.get('port')
        description = challenge_data.get('description')

        if not all([title, port, description]):
            flash(f'Incomplete challenge data! Skipping user because invalid format: {challenge_data}', 'warning')
            continue
        
        existing_challenge = Challenge.query.filter_by(title=title).first()
        if existing_challenge:
            flash('Challengem with title "{}" already exists! Skipping challenge.'.format(title), 'warning')
            continue
        
        existing_challenge = Challenge.query.filter_by(port=port).first()
        if existing_challenge:
            flash('Challengem with port "{}" already exists! Skipping challenge.'.format(port), 'warning')
            continue

        new_challenge = Challenge(title=title, port=port, description=description)
        db.session.add(new_challenge)

    db.session.commit()

    flash('Users imported successfully!', 'success')
    return redirect(url_for('challenges'))

@app.route('/challenge/export', methods=['GET'])
@login_required
def export_challenges():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenges = Challenge.query.all()
    challenge_data = [{'title': challenge.title, 'port': challenge.port ,'description': challenge.description} for challenge in challenges]
    
    json_data = json.dumps(challenge_data, indent=4)
    
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=challenges.json'}
    )
    
    return response