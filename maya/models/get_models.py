import requests
# download pyrite_v4.safetensors model
url = 'https://civitai.com/api/download/models/208431?type=Model&format=SafeTensor&size=pruned&fp=fp16'
response = requests.get(url)
with open('pyrite_v4.safetensors', 'wb') as f:
    f.write(response.content)


# download dreamshaper_8.safetensors model
url = 'https://civitai.com/api/download/models/128713?type=Model&format=SafeTensor&size=pruned&fp=fp16'
response = requests.get(url)
with open('dreamshaper_8.safetensors', 'wb') as f:
    f.write(response.content)


# download controlnet models
url = 'https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_normalbae.pth?download=true'
response = requests.get(url)
with open('control_v11p_sd15_normalbae.pth', 'wb') as f:
    f.write(response.content)

url = 'https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth?download=true'
response = requests.get(url)
with open('control_v11p_sd15_openpose.pth', 'wb') as f:
    f.write(response.content)