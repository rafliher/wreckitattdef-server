from flask import jsonify, render_template, request, flash, redirect, url_for
from app import app, db
from app.models import Tick, Flag, Challenge, Submission, Calculation, Config, User
from flask_login import login_required, current_user
import requests
import json
import random
import string
import os
from dotenv import load_dotenv

load_dotenv()

@app.route('/tick', methods=['GET'])
@login_required
def view_config():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    config = Config.query.first()
    if not config:
        config = Config()  # Create a new config if none exists

    # Fetch information about the last tick and its start time
    last_tick = Tick.query.order_by(Tick.id.desc()).first()
    last_tick_start_time = last_tick.created_at if last_tick else None

    return render_template('view_config.html', config=config, last_tick=last_tick, last_tick_start_time=last_tick_start_time)

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
    config.challenge_started = request.form.get('challenge_started') == 'true'
    config.ticks_count = int(request.form.get('ticks_count', 0))  # Ensure integer value
    config.tick_duration_seconds = int(request.form.get('tick_duration_seconds', 60))  # Ensure integer value

    db.session.add(config)
    db.session.commit()

    flash('Configuration updated successfully!', 'success')
    return redirect(url_for('view_config'))  # Redirect to view_config route or template

tick_started = False

def next_tick():
    # Get the last tick ID and insert +1 if it exists, otherwise insert 1
    last_tick = Tick.query.order_by(Tick.id.desc()).first()
    if last_tick:
        new_tick_id = last_tick.id + 1
    else:
        new_tick_id = 1

    # Generate team*chall flag and distribute each by POST /flag to node
    challenges = Challenge.query.all()
    users = User.query.filter_by(is_admin=False).all()  # Exclude admin users
    for challenge in challenges:
        for user in users:
            flag_value = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            flag_string = f'WreckIT5{{{flag_value}}}'  # Format the flag as required
            flag_distribution_url = f'http://{user.host_ip}/flag'
            try:
                response = requests.post(flag_distribution_url, json={'flag': flag_string, 'challenge_name': challenge.name})
                if response.status_code != 200:
                    return f"Failed to distribute flag for {challenge.name} to {user.host_ip}"

                # Save flag information to Flag model in database
                flag = Flag(
                    tick_id=new_tick_id,
                    user_id=user.id,
                    chall_id=challenge.id,
                    flag_value=flag_value
                )
                db.session.add(flag)
            except requests.RequestException as e:
                return f"An error occurred while distributing flag for {challenge.name} to {user.host_ip}: {str(e)}"

    # Commit all changes to the database
    db.session.commit()

    new_tick = Tick(id=new_tick_id)
    db.session.add(new_tick)
    db.session.commit()

    if last_tick:
        # Calculate scores and save to Calculation model
        for user in users:
            for challenge in challenges:
                # Calculate attack score
                success_attacks = Submission.query.filter_by(attacker=user, chall_id=challenge.id, tick_id=last_tick.id).count()
                attack_score = success_attacks

                # Calculate defense score
                failed_defenses = Submission.query.filter_by(target=user, chall_id=challenge.id, tick_id=last_tick.id).count()
                defense_score = 5 if failed_defenses == 0 else 0

                check_url = f'http://{user.host_ip}/check/{challenge.name}'
                try:
                    check_response = requests.post(check_url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))
                    if check_response.status_code == 200 and check_response.json().get('success'):
                        status = 'up'  # Success status
                    else:
                        status = 'error'  # Error status
                except requests.RequestException:
                    status = 'down'  # Error status if request fails

                # Save the calculated data to Calculation model
                calculation = Calculation(
                    attack=attack_score,
                    defense=defense_score,
                    status=status,
                    user_id=user.id,
                    chall_id=challenge.id,
                    tick_id=new_tick_id
                )
                db.session.add(calculation)

    # Commit all changes related to score calculations to the database
    db.session.commit()
    
    # Check if tick count in config is reached
    config = Config.query.first()
    if config and new_tick_id >= config.ticks_count:
        config.challenge_started = False
        db.session.commit()
        tick_started = False
        return f"Tick {new_tick_id} processed successfully. Challenge completed."

    return f"Tick {new_tick_id} processed successfully."
