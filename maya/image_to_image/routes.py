from flask import render_template, request, url_for, redirect, jsonify, flash

from maya import app, config, basedir, db
from maya.models.img2img_model import load_Model, generate_image
import io
import os
import secrets
from flask_login import current_user
from maya.payment.models import Payment
from maya.image_to_image.models import ImageToImage
from PIL import Image


global pipe
pipe = None
# pipe =  load_Model("pyrite_v4.safetensors")
@app.route("/imagetoimage", methods=['GET','POST'])
def imageToImage():
    
    global pipe
    
    if request.method == 'POST':
        
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
        
        
        prompt = request.form.get('description')
        model_type = request.form.get('model_type')
        image  = request.files.get('imageInput')
        
        if model_type=="option1":
            model_path = "pyrite_v4.safetensors"
        elif model_type=="option2":
            model_path = "dreamshaper_8.safetensors"
         
      
        if pipe:
            print("Model loaded successfully")
            return after_model_loaded(pipe, image, prompt, model_type)
        else:
            print("Model not loaded")
            pipe =  load_Model(model_path)
            return after_model_loaded(pipe, image, prompt, model_type)
    
    #   no_animation=True, image_url=image_url,
    #    prompt=prompt,model_type=model_type,
    #    input_image_path='static/photos/1.png'
    
    return render_template("image_to_image/image_to_image.html",  no_animation=False,                   
                           title=config.get('APP_NAME','image to image'),
                           app_name=config.get('APP_NAME','image to image')  )
    
    
def after_model_loaded(pipe, image, prompt, model_type):
    try:
            # save input image to database
            # input_image_path = f"{os.path.join(basedir, 'static', 'photos')}\{secrets.token_hex(10)}.png"
            input_image_path = os.path.join(basedir, 'static', 'photos', f"{secrets.token_hex(10)}.png")
            input_image=Image.open(io.BytesIO(image.read()))
            input_image.save(input_image_path)
            print(f"input_image_path : {input_image_path}")
            
            images = generate_image(pipe=pipe,control_image=input_image_path, prompt=prompt,
                                       num_inference_steps=20,)
            
            image_url = []
            image_paths= []
            
            image_name=secrets.token_hex(10)
            for index, image in enumerate(images):
                image_path = os.path.join(basedir, 'static', 'photos', f"{image_name}_{index:02d}.png")                
                url = url_for('static', filename='photos/' + os.path.basename(image_path))
                image.save(image_path)
                image_url.append(url)
                image_paths.append(image_path)
        
            print(image_url)
            
            # save data in database           
            
            unit = ImageToImage(user_id=current_user.id, prompt=prompt, input_image=input_image_path, generated_image=image_paths)
            db.session.add(unit)
            db.session.commit()
            print(f"image to image commit successful ")
            
             # update coins in account
            user_payment = Payment.query.filter_by(user_id=current_user.id).first()
            if user_payment:
                user_payment.current_coins = user_payment.current_coins - 3
                db.session.commit()
                print(f"payment update successful ")
            
            input_image_path=url_for('static', filename='photos/' + os.path.basename(input_image_path))
                        
            return render_template("image_to_image/image_to_image.html",
                                   no_animation=True, image_url=image_url,
                                   prompt=prompt,model_type=model_type,
                                   input_image_path=input_image_path,
                           title=config.get('APP_NAME','image to image'),
                           app_name=config.get('APP_NAME','image to image')  )
            
    except Exception as e:
        print(e)
        return render_template("image_to_image/image_to_image.html", no_animation=False,                         
                           title=config.get('APP_NAME','image to image'),
                           app_name=config.get('APP_NAME','image to image')  )      
            
@app.route("/loadmodel", methods=['POST'])
def loadModel():
    global pipe
    data = request.get_json()
    model_type = data.get('model_type')

  
    
    
    if model_type=="option1":
        model_type = "pyrite_v4.safetensors"
    elif model_type=="option2":
        model_type = "dreamshaper_8.safetensors"
        
    print(model_type)  
    pipe = load_Model(model_type)
    
    if pipe:
        print("Model loaded successfully")
    else:
        print("Model not loaded")
    
    # Process the model_type as needed
    # Placeholder for actual model loading logic
    response_data = {
        'success': True,
        'message': f'Model {model_type} loaded successfully'
    }
    return jsonify(response_data)