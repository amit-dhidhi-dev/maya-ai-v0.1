from maya import db, app
from datetime import datetime
from email.policy import default
from sqlalchemy import JSON

class ImageToImage(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, unique=False)
    prompt=db.Column(db.String(500), unique=False)
    input_image=db.Column(db.String(50), unique=False)
    generated_image= db.Column(JSON)
    date=db.Column(db.DateTime, unique=False, default=datetime.utcnow )
    
    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "prompt": self.prompt,
                "input_image":self.input_image, "generated_image":self.generated_image, 
                "date":self.date}


with app.app_context():
    db.create_all()