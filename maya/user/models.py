from flask_login import UserMixin

from maya import db, login_manager, app
# from maya.payment.models import Payment

@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)


class Register(db.Model, UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), unique=False)
    email=db.Column(db.String(100), unique=True)
    password=db.Column(db.String(200), unique=False)
    
    payment = db.relationship('Payment', backref='author', lazy=True, cascade="all, delete")



with app.app_context():
    db.create_all()