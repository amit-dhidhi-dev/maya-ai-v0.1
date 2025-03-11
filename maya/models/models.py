
from flask import Flask, request, jsonify
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
import os
import secrets
from maya import basedir

os.environ["HF_HOME"] = "G:/maya ai/test1/cache"

# app = Flask(__name__)

def load_model_for_text(model_path, use_gpu=False):
    
    model_path = os.path.join("maya/models", model_path)
    
    if use_gpu:
        pipe = StableDiffusionPipeline.from_single_file(model_path,
                                                        chache_dir="G:/maya ai/test1/cache",
                                                        torch_dtype=torch.float16)
        pipe = pipe.to("cuda")
    else:
        pipe = StableDiffusionPipeline.from_single_file(model_path,
                                                        chache_dir="G:/maya ai/test1/cache")
        pipe = pipe.to("cpu")
    
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    return pipe

def generate_image_from_text(pipe, prompt,
                   num_inference_steps=20,num_images_per_prompt=1,
                   width=512, height=512):
     
    images = pipe(prompt, width=width, height=height,
                  num_inference_steps=num_inference_steps,
                  num_images_per_prompt=num_images_per_prompt).images
    
    return images    

def generate_image(model_path, prompt, output_path,
                   num_inference_steps=20,num_images_per_prompt=1,
                   width=512, height=512,
                   use_gpu=False):
    model_path = os.path.join("maya/models", model_path)
    if use_gpu:
        pipe = StableDiffusionPipeline.from_single_file(model_path, torch_dtype=torch.float16)
        pipe = pipe.to("cuda")
    else:
        pipe = StableDiffusionPipeline.from_single_file(model_path)
        pipe = pipe.to("cpu")
    
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    images = pipe(prompt, width=width, height=height,
                  num_inference_steps=num_inference_steps,
                  num_images_per_prompt=num_images_per_prompt).images
    
    img_paths=[]
    
    for index, image in enumerate(images):
        image_path = os.path.join(basedir, 'static', 'photos', f"{secrets.token_hex(10)}.png")
        image.save(image_path)
        img_paths.append(image_path)
        
    return img_paths
        
