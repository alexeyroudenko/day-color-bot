#https://pygame.ru/blog/parsing-yandeks-kartinok-python.php

import re
import urllib.request
from bs4 import BeautifulSoup

def get_yandex_img_urls(query):
    url = f"https://yandex.ru/images/search?text={query}"
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    html = str(soup)
    url_extract_pattern = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
    urls = re.findall(url_extract_pattern, html)
    
    image_pattern = re.compile(r'.*\.(jpg|jpeg|png|gif|webp|bmp|tiff|svg)$', re.IGNORECASE)
    image_urls = list(filter(image_pattern.match, urls))

    for url in image_urls:
        print(url)
        
    return(image_urls)  
    
get_yandex_img_urls("Artist")