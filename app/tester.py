import requests
import time 
import random


f = open('./data/text_ru.txt', mode="r", encoding="utf-8")
texts = f.read()
words = texts.replace("\n", " ").replace(",", " ").split(' ')
song_words = []
for w in words:
    if len(w) > 4:
        song_words.append(w)
        word = w
        #url = f"http://localhost:5000/app_ctrl/add_word/{word}/"
        url = f"http://localhost:5000/tag_ctrl/tag_add/{word}/"
        print(url)
        #requests.get(url)        
        time.sleep(1)
        
print(song_words)