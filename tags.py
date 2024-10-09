import os
import click
import time
import re
from bs4 import BeautifulSoup
import logging
import logging.handlers
import pathlib

import time
import requests

from events import Event          


import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
    

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')  



'''
retrieve_trends
'''    
def retrieve_trends():
    current_url = "https://twitter-trends.iamrohit.in"
    response = requests.get(current_url, timeout=5)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    all_tags = soup.findAll('a', class_='tweet')
    tags = []
    for tag in all_tags:
        tags.append(tag.text)
    return tags

def save_trends(trends):
    import datetime
    file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    filename_textout  = pathlib.PurePath(cfg['app']['txt_path'] + file_base + ".txt").as_posix()
    logging.info(f"write state {filename_textout}")
    f = open(filename_textout, "w",  encoding="utf8")
    f.write("%s\n\n" % "world")
    f.write("%s\n\n" % "\n".join(trends))
    f.close()

'''
Tag class
created by tag string and store state of downloaded images and page
'''
class Tag():
    def __init__(self, tag_str:str):
        self.tag_str = tag_str
        self.count = -1
        # self.count_files = 0
        
    def ping(self):
        self.count += 1


'''
State class
hold list of tags, detect when add or delete tag
'''
class State():
    def __init__(self, event):
        self.tags = {}    
        self.event = event
        
    def update(self, new_tags):
        self.event.send("tags", "update", new_tags)
        for tag_str in new_tags:
            if tag_str in self.tags:
                tag = self.tags[tag_str]
                time.sleep(0.1)
                self.event.send("tag", "update", tag_str, tag.count)
                tag.ping()
            else:
                tag = Tag(tag_str)
                self.tags[tag_str] = tag
                time.sleep(0.1)
                self.event.send("tag", "add", tag_str)
                tag.ping()
                
        keys = list(self.tags.keys())
        for tag_str in keys:
            if tag_str not in new_tags:
                time.sleep(0.1)
                self.event.send("tag", "delete", tag_str)
                del self.tags[tag_str]
                
    def dump(self):
        for tag in self.tags.keys():
            logging.info(self.tags[tag].tag_str, self.tags[tag].count)
        return self.tags.keys()




from images import TagURLS
'''


'''
class AddToQueueCommand():
    def __init__(self, images):
        self.images = images            
        
    def execute(self, tag_str):
        self.tag_str = tag_str        
        self.tagURLS = TagURLS(tag_str)
        self.urls = self.tagURLS.retrieve(tag_str)
        count_files = 0
        folder = cfg['app']['tags_folder'] + self.tag_str + "/"
        if self.urls:
            for img_url in self.urls:
                count_files += 1
                out_file = folder + f"{count_files}.jpg"
                logging.info(f"queue add {img_url} to {out_file}")                        
                self.images.queue.put([img_url, out_file])
                
            if not self.images.started:
                self.images.start_thread()
'''


'''
class AddToQueueWordCommand():
    def __init__(self, images):
        self.images = images            
        
    def execute(self, tag_str):
        self.tag_str = tag_str        
        self.tagURLS = TagURLS(tag_str)
        self.urls = self.tagURLS.retrieve(tag_str)
        count_files = 0
        folder = cfg['app']['tags_folder'] + self.tag_str + "/"
        if self.urls:
            for img_url in self.urls:
                count_files += 1
                out_file = folder + f"{count_files}.jpg"
                logging.info(f"word_queue add {img_url} to {out_file}")                        
                self.images.word_queue.put([img_url, out_file])
                
            if not self.images.word_started:
                self.images.start_word_thread()
                
        # self.images.word_queue.join()
        
'''


'''
class MakeSpotCommand():
    def __init__(self):
        ...
        
    def execute(self, word):
        from spot import make_collages_folder
        from spot import make_spot
        collage_path = cfg['app']['tags_folder'] + f"{word}_src.jpg"
        make_collages_folder(cfg['app']['tags_folder'] + f"/{word}/", collage_path)
        spot_path = make_spot(collage_path, word, cfg['app']['spot_folder'])
                
'''


'''
from images import Images
from events import Observer
from events import OSCsender

class Runner():    
    def __init__(self):
        self.started = False
        
        self.event = Event()
        self.state = State(self.event)        
        self.observer = Observer(self.event)        
        self.observer.attach(self)
        
        self.osc = OSCsender()
        self.observer.attach(self.osc)
        
        self.images = Images(self.event)

    '''
        Listen Event Class events
        convert events to commands
    '''
    def on_event(self, args):
        logger.info(f"Runner on_event {args}")
        msg = args[0]
        
        if msg == "tag":
            action = args[1]
            if action == "add":
                tag = args[2]
                command = AddToQueueCommand(self.images)
                command.execute(tag)
                
        if msg == "word":
            action = args[1]
            if action == "finish":
                word = self.word_command.tag_str
                logger.info(f"make spot for {word}")
                command = MakeSpotCommand()
                command.execute(word)

    '''
        Regular logic
    '''
    def loop(self, trends):
        save_trends(trends)
        self.state.update(trends)

    '''
        Retrieve word from TG
    '''
    def process_msg(self, *args):
        word = args[0]
        self.event.send("msg", "process_msg", word)
        
        folder = cfg['app']['tags_folder'] + word + "/"
        os.makedirs(folder, exist_ok=True)
        
        command = AddToQueueWordCommand(self.images)
        command.execute(word)
        
        self.word_command = command        
        self.event.waiting_word = True