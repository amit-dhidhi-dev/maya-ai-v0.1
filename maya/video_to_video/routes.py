from flask import render_template, request, jsonify, url_for, redirect, flash

from maya import app, config, basedir, db
from maya.models.img2img_model import load_Model, generate_image
import cv2
from werkzeug.utils import secure_filename
import os
from moviepy import VideoFileClip, AudioFileClip
import secrets
import random
from flask_login import current_user
from maya.payment.models import Payment
from maya.video_to_video.models import VideoToVideo


global pipe
pipe = None
global seedAndFrameDict
seedAndFrameDict = {}

@app.route("/videotovideo" , methods=['GET','POST'])
def videoToVideo():
    
    global pipe
    global seedAndFrameDict
    global frames_path 
    global fps
    global duration
    global audio
    global frames_list
    global video_path
    if request.method == 'POST':
        
        
         # check  user log in 
        if not current_user.is_authenticated:
            flash("you are not log in",'danger')
            return redirect(url_for('home'))
        
        # check user payment
        user_payment = Payment.query.filter_by(user_id=current_user.id).first()        
        if user_payment:
            if user_payment.current_coins < 50:
                  flash("you do not have enough coins for this operation. ", "danger")
                  return redirect(url_for('payment'))
        else:
            flash("you do not have any plan now. ", "danger")
            return redirect(url_for('payment'))
        
        
        prompt = request.form.get('description')
        model_type = request.form.get('model_type')
        video  = request.files.get('videoFile')
        status  = request.form.get('checkbox')
        frameSrc  = request.form.get('selectFrameSrc')
        
        if model_type=="option1":
            model_path = "pyrite_v4.safetensors"
        elif model_type=="option2":
            model_path = "dreamshaper_8.safetensors"
        
        print(model_type, video, prompt, status, request.form) 
       
        if video or len(seedAndFrameDict) > 0:
            if len(seedAndFrameDict) == 0:
                print('inside the seed and frame dict')
                # save the video
                filename = secure_filename(f"{secrets.token_hex(8)}_{video.filename}")
                video_path  = os.path.join(basedir,'static','videos',filename)
                video.save(video_path)
            
                # get video info 
                frames_path, fps, duration, audio, frames_list = get_video_info(video_path)
                
                # check video duration is no longer than 10 seconds
                if duration > 10:
                    flash("Video duration is too long. Please upload a video with a duration of 10 seconds or less.", "danger")
                    return redirect(url_for('videoToVideo'))
                
                # check he has enough coins
                if user_payment.current_coins < (len(frames_path) * 3):
                    flash("you do not have enough coins for this operation. ", "danger")
                    return redirect(url_for('payment'))
             
            if status == "video":   
                print('generate video')
              
                seed = None
                if frameSrc:
                    seed = seedAndFrameDict[os.path.basename(frameSrc)]
                    seedAndFrameDict.clear()  
                if pipe:
                    print("Model loaded successfully")
                    return after_model_loaded(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path, seed)
                else:
                    print("Model not loaded")
                    pipe =  load_Model(model_path)
                    return after_model_loaded(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path, seed)
            else:
                 print("generate style first..")
                 if pipe:
                    print("Model loaded successfully")
                    return after_model_loaded_for_style(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path)
                 else:
                    print("Model not loaded")
                    pipe =  load_Model(model_path)
                    return after_model_loaded_for_style(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path)
    
    
                            
                            #   original_video='static/videos/short_video.mp4',
                            # # image_url=['static/photos/sd.png','static/photos/1_4.png'],  
                            #  generated_video='static/videos/short_video.mp4',
                            #    prompt='prompt',model_type='option2',     
        else:
            print('video not found')                   
    
    return render_template("video_to_video/video_to_video.html", no_animation=False,                     
                           title=config.get('APP_NAME','video to video'),
                           app_name=config.get('APP_NAME','video to video')  )




def after_model_loaded_for_style(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path):
 try:   
   
    global seedAndFrameDict 
    seedAndFrameDict = {}  
    frame_path = secrets.token_hex(10)
    frame_urls = []
    for i in range(4):
        seed = random.randint(0,1000000000000)
    
        frames = generate_image(pipe=pipe, control_image=frames_path[0], 
                             prompt=prompt,num_inference_steps=20, 
                             seed=seed) 
    
    
    # save frame path
        frame_path = os.path.join(basedir,'static','photos',f"{frame_path}_{i:04d}.png")
        frames[0].save(frame_path)
    
    
        frame_url = url_for('static', filename='photos/' + os.path.basename(frame_path))
        frame_urls.append(frame_url)
        seedAndFrameDict[os.path.basename(frame_path)]=seed
    
    
     # update coins in account
        user_payment = Payment.query.filter_by(user_id=current_user.id).first()
        if user_payment:
            user_payment.current_coins = user_payment.current_coins - (3 * 4)         
            db.session.commit()
    
    video_path_url=url_for('static', filename='videos/' + os.path.basename(video_path))
    
    return render_template("video_to_video/video_to_video.html", no_animation=True,
                           original_video=video_path_url, image_url=frame_urls,
                               prompt=prompt,model_type=model_type,                                 
                           title=config.get('APP_NAME','video to video'),
                           app_name=config.get('APP_NAME','video to video')  )

 except Exception as e:
        print(e)
        return render_template("video_to_video/video_to_video.html", no_animation=False, 
                           title=config.get('APP_NAME','video to video'),
                           app_name=config.get('APP_NAME','video to video')  )


def after_model_loaded(pipe, frames_path, fps, duration, audio, prompt, model_type, video_path, seed):
 try: 
    if seed is None:
        seed = random.randint(0,1000000000000)
    
    frames = [generate_image(pipe=pipe, control_image=frame, 
                             prompt=prompt,num_inference_steps=20, 
                             seed=seed) for frame in frames_path ] 
    
    
    # save all the generated frame to it's corresponding orginal frame path
    for frame, frame_path in zip(frames, frames_path):    
        frame[0].save(frame_path)
            
    # generate video from generated frames
    output_video_path = generate_video(frames_path, fps, duration, audio,frames_list)
    print(f"Generated video saved to {output_video_path}")
    
    
    # save data in database
    unit = VideoToVideo(user_id=current_user.id, input_video=video_path, generated_video=output_video_path)
    db.session.add(unit)
    db.session.commit()
    
    directory_path='maya/static/generated_videos'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # get url of both videos
    video_path = url_for('static', filename='videos/' + os.path.basename(video_path))
    output_video_path= url_for('static', filename='generated_videos/' + os.path.basename(output_video_path))

     # update coins in account
    user_payment = Payment.query.filter_by(user_id=current_user.id).first()
    if user_payment:
            user_payment.current_coins = user_payment.current_coins - (3 * len(frames_path))
            db.session.commit()
            
    video_path_url=url_for('static', filename='videos/' + os.path.basename(video_path))        
    
    return render_template("video_to_video/video_to_video.html", no_animation=True,
                           original_video=video_path_url, generated_video=output_video_path,
                               prompt=prompt,model_type=model_type,                                 
                           title=config.get('APP_NAME','video to video'),
                           app_name=config.get('APP_NAME','video to video')  )

 except Exception as e:
        print(e)
        return render_template("video_to_video/video_to_video.html", no_animation=False, 
                           title=config.get('APP_NAME','video to video'),
                           app_name=config.get('APP_NAME','video to video')  )


def get_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"FPS: {fps}, Total Frames: {total_frames}, Duration: {duration:.2f} seconds")

    frame_list = []
    frames = []
    frame_count = 0
    
    #  make frames directory if not available
    directory_path='maya/static/frames'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Read and save frames with error handling
    while True:
        ret, frame = cap.read()
        if not ret :
            break
            
        frame_path = os.path.join(basedir, 'static', 'frames', f"frame_{frame_count:04d}.png")
        cv2.imwrite(frame_path, frame)
        frame_list.append(frame_path)
        frames.append(frame)
        frame_count += 1
        
        if frame_count % 10 == 0:  # Progress update every 10 frames
            print(f"Processed {frame_count}/{total_frames} frames")

    cap.release()

     #  make frames directory if not available
    directory_path='maya/static/audio'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Extract audio using try-except block
    try:
        video = VideoFileClip(video_path)
        audio_path = os.path.join(basedir, 'static', 'audio', f"{secrets.token_hex(10)}.mp3")
        if video.audio is not None:
            video.audio.write_audiofile(audio_path)
            video.close()
        else:
            audio_path = None
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        audio_path = None

    print(f"Total frames processed: {frame_count}")
    return frame_list, fps, duration, audio_path, frames

def generate_video(frames_path, fps, duration, audio_path, frames_list):
    try:
        # Generate video from frames
        frame_height, frame_width, _ = cv2.imread(frames_path[0]).shape
        print(f"Frame Height: {frame_height}, Frame Width: {frame_width}")
        
        # Use H.264 codec instead of mp4v
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        
        output_video_path = os.path.join(basedir, 'static', 'generated_videos', f"{secrets.token_hex(10)}.mp4")
        
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        # Write frames to video with progress tracking
        total_frames = len(frames_path)
        for idx, frame_path in enumerate(frames_path):
            frame = cv2.imread(frame_path)
            if frame is not None:
                out.write(frame)
                if idx % 10 == 0:  # Progress update every 10 frames
                    print(f"Writing frame {idx + 1}/{total_frames}")
            os.remove(frame_path)
        
        out.release()

        # Add audio if available
        if audio_path:
            try:
                video = VideoFileClip(output_video_path)
                audio = AudioFileClip(audio_path)
                
                # Ensure audio duration matches video duration
                # if audio.duration > video.duration:
                #     audio = audio.subclip(0, video.duration)
                
                final_video = video.with_audio(audio)
                final_output_path = os.path.join(basedir, 'static', 'generated_videos', f"{secrets.token_hex(10)}.mp4")
                final_video.write_videofile(final_output_path)
                
                video.close()
                audio.close()
                final_video.close()
                
                # Clean up intermediate files
                os.remove(output_video_path)
                os.remove(audio_path)
                
                return final_output_path
            except Exception as e:
                print(f"Error adding audio: {str(e)}")
                return output_video_path
        
        return output_video_path
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        return None



@app.route("/loadvideomodel", methods=['POST'])
def loadvideomodel():
    global pipe
    data = request.get_json()
    model_type = data.get('model_type')

    if pipe:
        pipe=None
    
    
    if model_type=="option1":
        model_type = "pyrite_v4.safetensors"
    elif model_type=="option2":
        model_type = "dreamshaper_8.safetensors"

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