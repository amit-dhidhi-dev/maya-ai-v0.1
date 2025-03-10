from flask import render_template, request, jsonify, url_for, redirect, flash

from maya import app, config, photos, basedir, db
from maya.models.models import load_model_for_text, generate_image_from_text
import os
import secrets
from flask_login import current_user
from maya.payment.models import Payment
from maya.text_to_image.models import TextToImage

global pipe
pipe = None

@app.route("/texttoimage", methods=['GET', 'POST'])
def textToImage():
    
    global pipe
    
    if request.method=="POST":
        
        # check  user log in 
        if not current_user.is_authenticated:
            flash("you are not log in",'danger')
            return redirect(url_for('home'))
        
        # check user payment
        user_payment = Payment.query.filter_by(user_id=current_user.id).first()        
        if user_payment:
            if user_payment.current_coins < 10:
                  flash("you do not have enough coins for this operation. ", "danger")
                  return redirect(url_for('payment'))
        else:
            flash("you do not have any plan now. ", "danger")
            return redirect(url_for('payment'))
        
        
        data = request.form
        print(data)
        
        prompt = data.get('description')
        imageRatio = data.get('selectedRatio')       
        numberOfImages = data.get('numberOfImages')
        model_type = data.get('model_type_for_text')
        width = data.get('width')
        height = data.get('height')
        
        print(f"width: {width}, height: {height}, model_type: {model_type}")
        
        if model_type == "option1":
            model_path = "pyrite_v4.safetensors" 
        elif model_type == "option2":
            model_path = "dreamshaper_8.safetensors"
        
        if pipe:
            print("Model loaded successfully")
            return after_text_model_loaded(pipe,  prompt, int(numberOfImages), int(width), int(height), imageRatio, model_type)
        else:
            print("Model not loaded")
            pipe =  load_model_for_text(model_path)
            return after_text_model_loaded(pipe,  prompt, int(numberOfImages), int(width), int(height), imageRatio, model_type)       
                    
            
    return render_template("text_to_image/text_to_image.html", no_animation=False,                          
                           title=config.get('APP_NAME','text to image'),
                           app_name=config.get('APP_NAME','text to image')  )


def after_text_model_loaded(pipe,  prompt, numberOfImages, width, height, imageRatio, model_type):
    
    try:
        output_path = os.path.join(basedir, 'static', 'photos', secrets.token_hex(10))
        output_path=output_path+'.png'
        
        images = generate_image_from_text(pipe, prompt, 
                                   num_inference_steps=1,
                                   num_images_per_prompt=numberOfImages,
                                   width=width, height=height)
        
        image_paths=[]      
        image_name=secrets.token_hex(10)
        
        for index, image in enumerate(images):
            image_path = os.path.join(basedir, 'static', 'photos', f"{image_name}_{index:02d}.png")
            image.save(image_path)
            image_paths.append(image_path)
            
            
        print(f"image_path: {image_paths}")
        
        image_url = []
        
        for image_path in image_paths:
            url = url_for('static', filename='photos/' + os.path.basename(image_path))
            image_url.append(url)
        
        # add to database
        unit = TextToImage(user_id=current_user.id, prompt=prompt, generated_image=image_paths)
        db.session.add(unit)
        db.session.commit()
        
        # update coins in account
        user_payment = Payment.query.filter_by(user_id=current_user.id).first()
        if user_payment:
            user_payment.current_coins = user_payment.current_coins - 1
            db.session.commit()
            
        print(f"image_url: {image_url}")            
        # return jsonify(success=True, image_url=image_url)
        return render_template("text_to_image/text_to_image.html",
                               no_animation=True, image_url=image_url, ratio=imageRatio,
                               prompt=prompt, numberOfImages=numberOfImages, 
                               model_type=model_type,
                               title=config.get('APP_NAME','text to image'),
                       app_name=config.get('APP_NAME','text to image'))
        
    except Exception as e:
        print(e)
        return render_template("text_to_image/text_to_image.html", no_animation=False,                         
                           title=config.get('APP_NAME','text to image'),
                           app_name=config.get('APP_NAME','text to image')  )


@app.route("/loadmodelfortext", methods=['POST'])
def load_model_text():
    global pipe
    try:
        data = request.get_json()
        model_type = data.get('model_type')  # Changed from model_type_for_text
        
        print(f"model_type: {model_type}, data: {data}")
        
        if model_type == "option1":
            model_path = "pyrite_v4.safetensors" 
        elif model_type == "option2":
            model_path = "dreamshaper_8.safetensors"
        
        # Add artificial delay to show loading (remove in production)
        # import time
        # time.sleep(20)
        
        pipe = load_model_for_text(model_path)
        
        if pipe:
            print("Model loaded successfully")
        else:
            print("Model not loaded")
        
        
        
        response_data = {
            'success': True,
            'message': f'Model {model_type} loaded successfully'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load model'
        }), 500
