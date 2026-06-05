import requests
import time 
import random

pages = ["/" , "help", 'spots_page']
for page in pages:
    url = f"http://localhost:5000/app_ctrl/switch_page/{page}/"
    requests.get(url)
    time.sleep(5)
