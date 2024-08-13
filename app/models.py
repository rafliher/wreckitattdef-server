from flask_login import UserMixin
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
import json 
import pytz

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    host_ip = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    attacks = relationship("Submission", foreign_keys="[Submission.attacker_id]", cascade="all, delete")
    breachs = relationship("Submission", foreign_keys="[Submission.target_id]", cascade="all, delete")
    calculations = relationship("Calculation", cascade="all, delete")

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'host_ip': self.host_ip,
        }

    def __repr__(self):
        return json.dumps(self.serialize())
    
    def get_id(self):
        return str(self.id)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    submissions = relationship("Submission", cascade="all, delete")
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'name': self.name,
            'port': self.port,
            'description': self.description,
        }

    def __repr__(self):
        return json.dumps(self.serialize())

class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.Text, nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    
    round = relationship("Round", cascade="all, delete")
    user = relationship("User", cascade="all, delete")
    challenge = relationship("Challenge", cascade="all, delete")

class Tick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Jakarta')), nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'created_at': self.created_at
        }

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Jakarta')), nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'created_at': self.created_at
        }

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attacker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    
    attacker = relationship("User", foreign_keys=[attacker_id], overlaps="attacks", cascade="all, delete")
    target = relationship("User", foreign_keys=[target_id], overlaps="breachs", cascade="all, delete")
    challenge = relationship("Challenge", overlaps="submissions", cascade="all, delete")
    round = relationship("Round", cascade="all, delete")

class Check(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    tick_id = db.Column(db.Integer, db.ForeignKey('tick.id'))
    status = db.Column(db.String(255), nullable=False)
    
    user = relationship("User", foreign_keys=[user_id], overlaps="attacks", cascade="all, delete")
    challenge = relationship("Challenge", overlaps="submissions", cascade="all, delete")
    tick = relationship("Tick", cascade="all, delete")

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    
    user = relationship("User", overlaps="calculations", cascade="all, delete")
    challenge = relationship("Challenge", cascade="all, delete")
    round = relationship("Round", cascade="all, delete")
    
class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_started = db.Column(db.Boolean, default=False)
    ticks_count = db.Column(db.Integer, default=0)
    tick_duration_seconds = db.Column(db.Integer, default=60)  # Example: 60 seconds per tick
    tick_per_round = db.Column(db.Integer, default=5)  # Example: 60 seconds per tick

    def serialize(self):
        return {
            'id': self.id,
            'challenge_started': self.challenge_started,
            'ticks_count': self.ticks_count,
            'tick_duration_seconds': self.tick_duration_seconds,
            'tick_per_round': self.tick_per_round,
        }

    def __repr__(self):
        return "<Config(id=" + self.id + ", challenge_started=" + self.challenge_started + ", ticks_count=" + self.ticks_count + ", tick_duration_seconds=" + self.tick_duration_seconds + ")>"