from flask import  render_template, redirect, url_for, flash
from maya import app, basedir, config
from flask_login import current_user
from maya.text_to_image.models import TextToImage
from maya.image_to_image.models import ImageToImage
from maya.video_to_video.models import VideoToVideo
import os

@app.route('/gallery')
def gallery():
    """
    Gallery route to display generated images and videos.
    """
    # # Check if the user is logged in
    if current_user.is_authenticated:
        # Get the user's ID
        user_id = current_user.id
    else:
      flash('you are not login','danger')
      return redirect(url_for('home'))

    # Query the database for generated images and videos
    text_to_images = TextToImage.query.filter_by(user_id=user_id).all()
    image_to_image = ImageToImage.query.filter_by(user_id=user_id).all()
    video_to_video = VideoToVideo.query.filter_by(user_id=user_id).all()

    t2i_url = []
    t2i_images = {}
    i2i_url = []
    i2i_images = {}
    v2v_url = []
    v2v_videos = {}
    
    # get all the images in text to image generation
    if text_to_images:
       for t2i in text_to_images:
         t2i_url.clear()
         for image in t2i.generated_image:
           url = url_for('static',filename='photos/'+os.path.basename(image))
           t2i_url.append(url)
         t2i_images[t2i.id]=t2i_url
    
    # get all the image in image to image generation  
    if image_to_image:
       for i2i in image_to_image:
         i2i_url.clear()
         input_url = url_for('static',filename='photos/'+os.path.basename(i2i.input_image))
         for image in i2i.generated_image:
            url = url_for('static',filename='photos/'+os.path.basename(image))
            i2i_url.append(url)
         i2i_images[i2i.id]=[input_url, i2i_url]
      
    #  get all the video in video to video generation
    if video_to_video:
      for v2v in video_to_video: 
         original_video = url_for('static',filename='videos/'+os.path.basename(v2v.input_video))
         generated_video = url_for('static',filename='generated_videos/'+os.path.basename(v2v.generated_video))
         v2v_videos[v2v.id]=[original_video,generated_video]
      
    # Render the gallery template with the retrieved data
    return render_template('gallery/gallery.html',
                              gallery='gallery',
                               text_to_images=text_to_images, image_to_image=image_to_image, 
                               video_to_video=video_to_video, t2i_images=t2i_images,i2i_images=i2i_images,
                               v2v_videos=v2v_videos, 
                               title=config.get('APP_NAME','video to video'),
                                app_name=config.get('APP_NAME','video to video')  
                                )