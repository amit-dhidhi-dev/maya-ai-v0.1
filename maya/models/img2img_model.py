import torch
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
    DPMSolverMultistepScheduler
)
from PIL import Image
import numpy as np
import os
import  math
import secrets

os.environ["HF_HOME"] = "G:/maya ai/test1/cache"

current_model = None

def load_Model(model_name, use_gpu=False):
    """Set up the Stable Diffusion pipeline with ControlNet from local files."""
    global current_model
   
    try:
       
       if current_model is not None:
           del current_model
           if torch.cuda.is_available():
               torch.cuda.empty_cache()
       
       c1= os.path.join("maya/models", "control_v11p_sd15_normalbae.pth")
       c2= os.path.join("maya/models", "control_v11p_sd15_openpose.pth")
       controlnet_paths = [c1, c2]
       base_model_path = os.path.join("maya/models", model_name)  
        
       controlnets = [ControlNetModel.from_single_file(
            path
        ) for path in controlnet_paths]
        # Initialize pipeline from local files
        
       if use_gpu:
           pipe = pipe = StableDiffusionControlNetPipeline.from_single_file(
            base_model_path,
            controlnet=controlnets,
            chache_dir="G:/maya ai/test1/cache",
            torch_dtype=torch.float16,
        )
           pipe = pipe.to("cuda")
       else:
           pipe = pipe = StableDiffusionControlNetPipeline.from_single_file( base_model_path,
            controlnet=controlnets,
            chache_dir="G:/maya ai/test1/cache",)
           
           pipe = pipe.to("cpu")
        

        # Use better scheduler
    #    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
       
    #    this is DPM2++ keraas scheduler
       pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True )
    
       
       
       current_model = pipe

       return pipe
    except Exception as e:
        print(f"Error loading models: {str(e)}")




def resize_image_proportionally(original_width, original_height, target_size=512):
    ratio = min(target_size / original_width, target_size / original_height)    
    # Calculate the new dimensions
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return new_width, new_height


def load_image(image_path):
    """Load and preprocess input image."""
    image = Image.open(image_path)

    width, height = image.size
    print(f'width:{width}, height:{height}')

    width, height = resize_image_proportionally(width, height)

    image = image.convert("RGB")
    # image = image.resize((width, height))
    image = image.resize((512, 512))
    # image = np.array(image)
    return image , width, height





def generate_image(
    pipe,
    control_image,
    prompt,
    negative_prompt="",
    num_inference_steps=20,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0,
    seed=None,
    strength=0.8,
    width=512,
    height=512,
):
    """Generate image using Stable Diffusion with ControlNet guidance."""
    if seed is not None:
        torch.manual_seed(seed)
        print(seed)
        num_images_per_prompt = 1
    else:   
        num_images_per_prompt = 4

    # Generate image
    # output = pipe(
    #     prompt=prompt,
    #     negative_prompt=negative_prompt,
    #     image=control_image,
    #     num_inference_steps=num_inference_steps,
    #     guidance_scale=guidance_scale,
    #     controlnet_conditioning_scale=controlnet_conditioning_scale,
    #     strength=strength,
    # ).images[0]
    
    
    control_image, width, height = load_image(control_image)
    w, h = Image.open(control_image).size
    if w>512 or h>512 :
      width=w
      height=h

    
    negative_prompt = "low quality, blurry, bad art"
    print(prompt)

    output = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=[control_image, control_image],  # Provide the same control image for each ControlNet
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        controlnet_conditioning_scale=controlnet_conditioning_scale,
        strength=strength,
        num_images_per_prompt=num_images_per_prompt,
        width=width,
        height=height,
    ).images

    print(f'width:{width}, height:{height} before output')
    return output





