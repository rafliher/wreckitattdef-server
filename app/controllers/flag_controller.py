from flask import Blueprint, request, jsonify
from app import app, db
from app.models import Tick, Flag, Submission, User, Challenge, Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import pytz

@app.route('/api/flag', methods=['POST'])
@jwt_required()
def submit_flag():
    username = get_jwt_identity()['username']
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    config = Config.query.first()
    if not (config and config.challenge_started):
        return jsonify({"message": "Challenge is not started"}), 400

    data = request.get_json()
    if not data or 'flag' not in data:
        return jsonify({"message": "Invalid data"}), 400

    flag_value = data['flag']

    # Get the current tick
    current_tick = Tick.query.order_by(Tick.id.desc()).first()
    if not current_tick:
        return jsonify({"message": "No current tick found"}), 404

    # Check if the flag matches the flag in the table for the current tick
    flag = Flag.query.filter_by(
        string=flag_value,
        tick_id=current_tick.id
    ).first()

    if not flag:
        return jsonify({"message": "Invalid flag"}), 400

    # Check if the flag is for a different user (target)
    if flag.user_id == user.id:
        return jsonify({"message": "Cannot submit your own flag"}), 400
    
    # Check if the flag has already been submitted by the same user
    existing_submission = Submission.query.filter_by(
        tick_id=current_tick.id,
        chall_id=flag.chall_id,
        attacker_id=user.id,
        target_id=flag.user_id,
    ).first()

    if existing_submission:
        return jsonify({"message": "Flag has already been submitted"}), 400

    # Insert into Submission table
    submission = Submission(
        tick_id=current_tick.id,
        chall_id=flag.chall_id,
        attacker_id=user.id,
        target_id=flag.user_id,
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "Flag submitted successfully"}), 200
