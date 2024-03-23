from flask_login import UserMixin
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
import json 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    host_ip = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    attacks = relationship("Submission", foreign_keys="[Submission.attacker_id]")
    breachs = relationship("Submission", foreign_keys="[Submission.target_id]")
    calculations = relationship("Calculation")

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
    title = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    submissions = relationship("Submission")
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'port': self.port,
            'description': self.description,
        }

    def __repr__(self):
        return json.dumps(self.serialize())

class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    string = db.Column(db.Text, nullable=False)
    tick_id = db.Column(db.Integer, db.ForeignKey('tick.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    
    tick = relationship("Tick")
    user = relationship("User")
    challenge = relationship("Challenge")

class Tick(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attacker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    tick_id = db.Column(db.Integer, db.ForeignKey('tick.id'))
    
    attacker = relationship("User", foreign_keys=[attacker_id], overlaps="attacks")
    target = relationship("User", foreign_keys=[target_id], overlaps="breachs")
    challenge = relationship("Challenge", overlaps="submissions")
    tick = relationship("Tick")
    
class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chall_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    tick_id = db.Column(db.Integer, db.ForeignKey('tick.id'))
    
    user = relationship("User", overlaps="calculations")
    challenge = relationship("Challenge")
    tick = relationship("Tick")
    
    
