import json
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES,UploadSet, configure_uploads, patch_request_class
import razorpay



app = Flask(__name__)

# razorpay integration
client = razorpay.Client(auth=("rzp_test_kAGBcIJrGmwmEf", "liJJBImHnZpNpH0UJ97ikT44"))


# Load the config.json file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

app.config["SQLALCHEMY_DATABASE_URI"] = config.get("SQLALCHEMY_DATABASE_URI","")
app.config['SECRET_KEY']=config.get('SECRET_KEY','paste_secret_key_here')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(basedir,'static')  # Base directory for uploads
app.config['UPLOADS_PHOTOS_DEST'] = 'static/photos'  # Folder for photos upload set

photos = UploadSet('photos', IMAGES)  # Define the 'photos' upload set
configure_uploads(app, photos)

patch_request_class(app)


db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = U"Please Login first."

from maya.user import  routes
from maya.payment import routes
from maya.dashboard import routes
from maya.text_to_image import routes
from maya.image_to_image import routes
from maya.video_to_video import routes