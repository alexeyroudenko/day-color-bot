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