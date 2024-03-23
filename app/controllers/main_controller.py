# app/controllers/main_controller.py

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app import app, db
from app.models import User, Challenge
from sqlalchemy import func

import os
from dotenv import load_dotenv
import json


@app.route('/dashboard')
@login_required
def dashboard():
    challenges = Challenge.query.all()

    return render_template('dashboard.html', challenges=challenges)

# @app.route('/scoreboard')
# def scoreboard():
#     users = User.query.all()
#     question_count = db.session.query(Question).count()
    
#     user_data = []
#     for user in users:
#         completions = db.session.query(user_question_association).filter_by(user_id=user.id).all()
#         user_data.append({
#             'user': user,
#             'progress': len(completions) / question_count,
#             'last_completion': max([completion.completion_time for completion in completions], default=None)
#         })

#     sorted_users = sorted(user_data, key=lambda x: (x['progress'], reversor(x['last_completion']) or datetime.min ), reverse=True)

#     return render_template('scoreboard.html', users=sorted_users)
