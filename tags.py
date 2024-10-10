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

from images import ItemDownload

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
    return tags[0:cfg['app']['count_trends']]

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
        self.folder = cfg['app']['tags_folder'] + self.tag_str + "/"        
        self.count = 0 # count updates of tag        
        self.page = 0 # page in bing for resuming adding images
        
    def ping(self):
        self.count += 1

    def save(self):
        self.cfg_file = cfg['app']['tags_folder'] + "/" + self.tag_str + ".cfg"
        print(f"------- save {self.cfg_file}")
        f = open(self.cfg_file, "w")
        f.write(str(self.count))
        f.write("\n")
        f.write(str(self.page))
        f.close()
        
    def load(self):
        self.cfg_file = cfg['app']['tags_folder'] + "/" + self.tag_str + ".cfg"
        print(f"------- load {self.cfg_file}")
        if os.path.isfile(self.cfg_file):            
            f = open(self.cfg_file, "r")
            lines = f.readlines()            
            self.count = int(lines[0])
            self.page = int(lines[1])
            print(f"load Tag {self.tag_str} {self.count} {self.page}")
            f.close()
        

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
                tag.load()
                time.sleep(0.1)
                self.event.send("tag", "update", tag_str, tag.count)
                tag.ping()
            else:
                tag = Tag(tag_str)
                self.tags[tag_str] = tag
                tag.load()
                time.sleep(0.1)
                self.event.send("tag", "add", tag_str)
                tag.ping()
                
        keys = list(self.tags.keys())
        for tag_str in keys:
            if tag_str not in new_tags:
                tag = self.tags[tag_str]
                tag.save()
                time.sleep(0.1)
                self.event.send("tag", "delete", tag_str)
                del self.tags[tag_str]
                
    def save(self):
        for tag in self.tags.keys():
            logging.info(f"save state {tag}")
            self.tags[tag].save()
                
    def dump(self):
        logging.info(f"tags:")
        for tag_key in self.tags.keys():
            tag:Tag = self.tags[tag_key]            
            logging.info(f"{tag.tag_str} count:{str(tag.count)} page:{str(tag.page)}")
            
        logging.info(f"------tags end")
        return self.tags.keys()




from images import TagURLS
'''


'''
class AddToQueueCommand():
    def __init__(self, images):
        self.images = images            
        
    def execute(self, tag:Tag):
        self.tag_str = tag.tag_str        
        self.tagURLS = TagURLS(tag.tag_str)
        self.urls, debug, request_url = self.tagURLS.retrieve(tag.count)
        count_files = tag.count * 10
        folder = cfg['app']['tags_folder'] + self.tag_str + "/"
        os.makedirs(folder, exist_ok=True)
        if self.urls:
            for img_url in self.urls:
                out_file = folder + f"{count_files}.jpg"
                item = ItemDownload(img_url, out_file, self.tag_str, request_url, debug)                                                     
                if count_files < 2:
                    # fast download for making spot                    
                    logging.info(f"fast queue add {img_url} to {out_file}")                        
                    self.images.trends_queue.put(item)
                else:
                    # detail download for analyze                    
                    logging.info(f"regular queue add {img_url} to {out_file}")                        
                    self.images.queue.put(item)
                count_files += 1
                
            if not self.images.trends_started:
                self.images.start_trends_thread()
                
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
        self.urls, debug, request_url = self.tagURLS.retrieve(tag_str)
        count_files = 0
        folder = cfg['app']['tags_folder'] + self.tag_str + "/"
        if self.urls:
            for img_url in self.urls:
                count_files += 1
                out_file = folder + f"{count_files}.jpg"
                item = ItemDownload(img_url, out_file, self.tag_str, request_url, debug)  
                logging.info(f"word_queue add {img_url} to {out_file}")                        
                self.images.word_queue.put(item)
                
            if not self.images.word_started:
                self.images.start_word_thread()
                
        # self.images.word_queue.join()
        
'''


'''
class MakeSpotCommand():
    def __init__(self):
        ...        
    def execute(self, word):
        ...
#         from spot import make_collages_folder
#         from spot import make_spot
#         collage_path = cfg['app']['spot_folder'] + f"{word}_src.jpg"
#         make_collages_folder(cfg['app']['tags_folder'] + f"/{word}/", collage_path)
#         spot_path = make_spot(collage_path, word, cfg['app']['spot_folder'])
        
'''


'''
class MakeTrendsSpotCommand():
    def __init__(self):
        ...        
    def execute(self, tags):
        import glob
        imgs = []
        for tag_key in tags.keys():
            tag = tags[tag_key]
            im = glob.glob(tag.folder + "*")            
            imgs.extend(im)
            
        import datetime
        file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')          
        word = file_base                  
        
#         from spot import make_collages
#         from spot import make_spot
#         collage_path = cfg['app']['spot_folder'] + f"{word}_src.jpg"
#         make_collages(imgs, collage_path)
#         spot_path = make_spot(collage_path, word, cfg['app']['spot_folder'])        
                
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
        # logger.info(f"Runner on_event {args}")
        msg = args[0]
        
        
        if msg == "data":
            action = args[1]
            if action == "downloaded":
                data: ItemDownload = args[2]
                #print(f"data: {data.toString()}")
            
        if msg == "tag":
            action = args[1]
            if action == "add":
                tag_str = args[2]
                command = AddToQueueCommand(self.images)
                command.execute(self.state.tags[tag_str])

            if action == "update":
                logger.info(f"update tag {args}")
                tag_str = args[2]
                command = AddToQueueCommand(self.images)
                command.execute(self.state.tags[tag_str])   
                
        if msg == "tags":
            # finised downloading bath            
            action = args[1]
            if action == "finish":
                logger.info(f"restarting collect {args}")
                self.state.dump()
                keys = list(self.state.tags.keys())                
                for tag_str in keys:
                    tag = self.state.tags[tag_str]
                    tag.ping()
                    self.event.send("tag", "update", tag_str, tag.count)
                    logger.info(f"restarting collect {tag}")
            if action == "downloaded":
                logger.info(f"tags downloaded {args}")
                                                                                                    
        if msg == "word":
            action = args[1]
            if action == "finish":
                word = self.word_command.tag_str
                # logger.info(f"make spot for {word}")
                command = MakeSpotCommand()
                command.execute(word)

        if msg == "trends":
            action = args[1]
            if action == "downloaded":
                logger.info(f"collect filenames")
                
            if action == "finish":
                # logger.info(f"make spot for trends")
                command = MakeTrendsSpotCommand()
                command.execute(self.state.tags)

    '''
        Regular logic
    '''
    def loop(self, trends):
        save_trends(trends)
        self.state.update(trends)
        self.state.save()
        

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