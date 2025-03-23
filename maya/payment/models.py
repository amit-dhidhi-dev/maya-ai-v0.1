from maya import db, app
from datetime import datetime
from email.policy import default
from maya.user.models import Register

class Payment(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    # user_id=db.Column(db.Integer, unique=True)
    current_coins=db.Column(db.Integer, unique=False)
    date=db.Column(db.DateTime, unique=False, default=datetime.utcnow )
    
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)


with app.app_context():
    db.create_all()