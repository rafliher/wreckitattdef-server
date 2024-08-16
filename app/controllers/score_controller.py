from flask import Blueprint, request, jsonify
from app import app, db
from app.models import User, Calculation, Challenge, Tick, Round, Submission, Check
from flask_jwt_extended import jwt_required

@app.route('/api/scoreboard', methods=['GET'])
@jwt_required()
def get_scoreboard():
    users = User.query.filter_by(is_admin=False).all()
    challenges = Challenge.query.all()
    scoreboard = []
    last_round = Round.query.order_by(Round.id.desc()).first()

    for user in users:
        user_scores = {
            "username": user.username,
            "is_defending_champion": False,  # Assuming you have a way to determine this
            "total_points": 0,
            "attack_points": 0,
            "defense_points": 0,
            "attacks": {},
            "defenses": {},
            "flags": {},
            "sla": {},
            "passed_checks": {},
            "total_checks": {}
        }
        
        for challenge in challenges:
            # Calculate attack score
            success_attacks = Submission.query.filter_by(attacker=user, chall_id=challenge.id).count()

            # Calculate defense score
            failed_defenses = Submission.query.filter_by(target=user, chall_id=challenge.id).count()
            total_round = (last_round.id if last_round else 1)
            defense_score = ((len(users) - 1) * total_round) - failed_defenses
            
            user_scores["attacks"][challenge.name] = success_attacks
            user_scores["defenses"][challenge.name] = defense_score
            user_scores["flags"][challenge.name] = {"captured": success_attacks, "stolen": failed_defenses}
            user_scores["sla"][challenge.name] = "DOWN"
            user_scores["passed_checks"][challenge.name] = 0
            user_scores["total_checks"][challenge.name] = 0

        checks = Check.query.filter_by(user_id=user.id).order_by(Check.tick_id.asc()).all()
        passed_checks = 0
        total_checks = 0

        for check in checks:
            challenge_name = Challenge.query.get(check.chall_id).name
            
            user_scores["total_checks"][challenge_name] += 1

            if check.status == "up":
                user_scores["passed_checks"][challenge_name] += 1

            user_scores["sla"][challenge_name] = check.status.upper()

        attack_points = 0
        defense_points = 0

        for challenge in challenges:            
            challenge_name = challenge.name
            attack_points += user_scores["attacks"][challenge_name]
            defense_points += user_scores["defenses"][challenge_name]
            
            passed_checks += user_scores["passed_checks"][challenge_name]
            total_checks += user_scores["total_checks"][challenge_name]
            
        
        availability_score = max(0.1, passed_checks / total_checks if total_checks > 0 else 0)
            
        user_scores["total_points"] = (attack_points + defense_points) * availability_score
        user_scores["attack_points"] = attack_points
        user_scores["defense_points"] = defense_points

        scoreboard.append(user_scores)

    return jsonify(scoreboard), 200
