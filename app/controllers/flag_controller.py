from flask import Blueprint, request, jsonify
from app import app, db, socketio  
from app.models import Tick, Flag, Submission, User, Challenge, Config, Round, FailedSubmission
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

    if user.is_admin:
        return jsonify({"message": "Admin do not play"}), 404
    
    config = Config.query.first()
    if not (config and config.challenge_started):
        return jsonify({"message": "Challenge is not started"}), 400

    data = request.get_json()
    if not data or 'flag' not in data:
        return jsonify({"message": "Invalid data"}), 400

    flag_value = data['flag']
    print("[" + str(datetime.now(pytz.timezone('Asia/Jakarta'))) + "] User " + username + " submit " + flag_value)

    # Get the current tick
    current_tick = Tick.query.order_by(Tick.id.desc()).first()
    if not current_tick:
        return jsonify({"message": "No current tick found"}), 404

    # Get the current tick
    current_round = Round.query.order_by(Round.id.desc()).first()
    if not current_round:
        return jsonify({"message": "No current round found"}), 404
    
    # Check if the flag matches the flag in the table for the current tick
    flag = Flag.query.filter_by(
        string=flag_value,
        round_id=current_round.id
    ).first()

    if not flag:
        return jsonify({"message": "Invalid flag"}), 400

    # Check if the flag is for a different user (target)
    if flag.user_id == user.id:
        return jsonify({"message": "Cannot submit your own flag"}), 400
    
    # Check if the flag has already been submitted by the same user
    existing_submission = Submission.query.filter_by(
        round_id=current_round.id,
        chall_id=flag.chall_id,
        attacker_id=user.id,
        target_id=flag.user_id,
    ).first()

    if existing_submission:
        return jsonify({"message": "Flag has already been submitted"}), 400

    # Insert into Submission table
    submission = Submission(
        round_id=current_round.id,
        chall_id=flag.chall_id,
        attacker_id=user.id,
        target_id=flag.user_id,
    )

    db.session.add(submission)
    db.session.commit()
    
    socketio.emit('flag_submitted', {
        'attacker': username,
        'target': flag.user.username,  # Assuming the User model has a username field
        'challenge': flag.challenge.name,  # Assuming Challenge model has a title field
        'timestamp': datetime.utcnow().isoformat()
    })

    return jsonify({"message": "Flag submitted successfully"}), 200
