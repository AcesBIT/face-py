from genericpath import isfile
import requests
import re
import os
from bs4 import BeautifulSoup

cwd = os.getcwd()
img_dir = os.chdir(cwd+"\\images")

url = input("Provide URL : ")

result = requests.get(url)
soup = BeautifulSoup(result.text,"html.parser")
images = soup.find_all("img")
id = 0
image_links = {} 
for image in images:
    src = image['src']
    if "https://" not in image['src']:
        src.lstrip("https://")
        src.lstrip("//")
        src.lstrip("/")
        src = "https://" + src

    image_links[id]={"img_id":f"image{id}","link":src}
    with open(os.getcwd()+"\\"+ image_links[id]["img_id"] + ".jpg",'wb') as f :
        try:
            im = requests.get(src)
            f.write(im.content)
            id += 1
        except:
            id += 1
            continue