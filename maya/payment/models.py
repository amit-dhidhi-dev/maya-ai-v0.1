from maya import db, app
from datetime import datetime
from email.policy import default


class Payment(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, unique=True)
    current_coins=db.Column(db.Integer, unique=False)
    date=db.Column(db.DateTime, unique=False, default=datetime.utcnow )
    


with app.app_context():
    db.create_all()