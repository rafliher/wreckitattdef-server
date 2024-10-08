from flask import jsonify, render_template, request, flash, redirect, url_for
from app import app, db
from app.models import Tick, Flag, Challenge, Submission, Config, User, Round, Check
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required
import requests
import json
import random
import string
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

@app.route('/api/round', methods=['GET'])
def api_round():
    config = Config.query.first()
    if not config:
        config = Config()
        
    last_round = Round.query.order_by(Round.id.desc()).first()
    last_tick = Tick.query.order_by(Tick.id.desc()).first()
    if last_round:
        last_round = last_round.serialize()
    if last_tick:
        last_tick = last_tick.serialize()
    return jsonify({"config": config.serialize(), "last_round": last_round, "last_tick": last_tick}), 200

@app.route('/round', methods=['GET'])
@login_required
def view_config():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    config = Config.query.first()
    if not config:
        config = Config()  # Create a new config if none exists

    # Fetch information about the last tick and its start time
    last_round = Round.query.order_by(Round.id.desc()).first()
    last_round_start_time = last_round.created_at if last_round else None
    last_tick = Tick.query.order_by(Tick.id.desc()).first()
    last_tick_start_time = last_tick.created_at if last_tick else None

    return render_template('view_config.html', config=config, last_round=last_round, last_round_start_time=last_round_start_time, last_tick=last_tick, last_tick_start_time=last_tick_start_time)

@app.route('/update_config', methods=['POST'])
@login_required
def update_config():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    config = Config.query.first()
    if not config:
        config = Config()  # Create a new config if none exists

    # Update config values based on the form or JSON data
    isStartingChallenge = request.form.get('challenge_started') == 'true'
    
    config.challenge_started = isStartingChallenge
    if request.form.get('ticks_count'):
        config.ticks_count = int(request.form.get('ticks_count', 0))  # Ensure integer value
    if request.form.get('tick_duration_seconds'):
        config.tick_duration_seconds = int(request.form.get('tick_duration_seconds', 60))  # Ensure integer value
    if request.form.get('tick_per_round'):
        config.tick_duration_seconds = int(request.form.get('tick_per_round', 60))  # Ensure integer value
        
    db.session.add(config)
    db.session.commit()
    
    if isStartingChallenge:
        print(next_tick())

    flash('Configuration updated successfully!', 'success')
    return redirect(url_for('view_config'))  # Redirect to view_config route or template

def next_tick():
    # Get the last tick ID and insert +1 if it exists, otherwise insert 1
    last_tick = Tick.query.order_by(Tick.id.desc()).first()
    if last_tick:
        new_tick_id = last_tick.id + 1
    else:
        new_tick_id = 1
        
    print("[" + str(pytz.timezone('Asia/Jakarta').localize(datetime.now())) + "] Tick " + str(new_tick_id) + " started")

    # Check if tick count in config is reached
    config = Config.query.first()
    if config and new_tick_id > config.ticks_count:
        config.challenge_started = False
        db.session.commit()
        return "[" + str(pytz.timezone('Asia/Jakarta').localize(datetime.now())) + "] Final tick reached. Challenge completed."

    new_tick = Tick(id=new_tick_id, created_at=pytz.timezone('Asia/Jakarta').localize(datetime.now()))
    db.session.add(new_tick)
    db.session.commit()
    
    challenges = Challenge.query.all()
    users = User.query.filter_by(is_admin=False).all()  # Exclude admin users

    # check challenge status
    for user in users:
        for challenge in challenges:
            check_url = 'http://' + user.host_ip + '/check/' + challenge.name
            try:
                check_response = requests.get(check_url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))
                if check_response.status_code == 200 and check_response.json().get('success'):
                    status = 'up'  # Success status
                else:
                    status = 'error'  # Error status
            except requests.RequestException:
                status = 'down'  # Error status if request fails

            check = Check(
                status=status,
                user_id=user.id,
                chall_id=challenge.id,
                tick_id=new_tick_id
            )
            db.session.add(check)

        db.session.commit()

    # call every 5 tick
    if new_tick_id % 5 == 1:
        last_round = Round.query.order_by(Round.id.desc()).first()
        if last_round:
            new_round_id = last_round.id + 1
        else:
            new_round_id = 1
            
        new_round = Round(id=new_round_id, created_at=pytz.timezone('Asia/Jakarta').localize(datetime.now()))
        db.session.add(new_round)
        db.session.commit()
            
        # Generate team*chall flag and distribute each by POST /flag to node
        for challenge in challenges:
            for user in users:
                flag_value = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
                flag_string = 'WreckIT50{' + flag_value + '}'  # Format the flag as required
                flag_distribution_url = 'http://' + user.host_ip + '/flag'
                try:
                    response = requests.post(flag_distribution_url, json={'flag': flag_string, 'challenge': challenge.name}, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))
                    if response.status_code != 200:
                        print("Failed to distribute flag for " + challenge.name + " to " + user.host_ip)
                    else:
                        print("Distributed flag for " + challenge.name + " to " + user.host_ip)

                    # Save flag information to Flag model in database
                    flag = Flag(
                        round_id=new_round_id,
                        user_id=user.id,
                        chall_id=challenge.id,
                        string=flag_value
                    )
                    db.session.add(flag)
                except requests.RequestException as e:
                    print ("An error occurred while distributing flag for " + challenge.name + " to " + user.host_ip + ": " + str(e))

        # Commit all changes to the database
        db.session.commit()

    return "[" + str(pytz.timezone('Asia/Jakarta').localize(datetime.now())) + f'] Tick {new_tick_id} processed successfully.'

@app.route('/reset_challenge', methods=['POST'])
@login_required
def reset_challenge():
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Remove all Submission, Check, and Tick data
    try:
        Submission.query.delete()
        Check.query.delete()
        Flag.query.delete()
        Tick.query.delete()
        Round.query.delete()
        
        config = Config.query.first()
        if not config:
            config = Config()  # Create a new config if none exists

        # Update config values based on the form or JSON data
        config.challenge_started = False

        db.session.add(config)
        db.session.commit()
        
        flash('Challenge data reset successfully.', 'success')
    except Exception as e:
        print(e)
        
        db.session.rollback()
        flash('An error occurred while resetting the challenge data: ' + str(e), 'danger')

    return redirect(url_for('view_config'))