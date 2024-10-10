import os
import numpy as np
from colors.colors import get_colours
from colors.colors import plot_colors2
from colors.som import get_som
from PIL import Image, ImageFilter, ImageFile

import re
import urllib.error
import urllib.request

from threading import Thread
from queue import Empty, Queue, LifoQueue

import logging
import logging.handlers

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('bot')  

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
    

headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
timeout = 1

# def save_image(self, link, file_path):
#     link2 = link.encode('ascii', 'ignore').decode('ascii')
#     request = urllib.request.Request(link2, None, headers)
#     image = urllib.request.urlopen(request, timeout=timeout).read()
#     if not imghdr.what(None, image):
#         print('[Error]Invalid image, not saving {}'.format(link2))
#         raise
#     with open(file_path, 'wb') as f:
#         f.write(image)

class ItemDownload():
    def __init__(self, url, dst, tag_str, request_url, debug):
        self.url = url
        self.dst = dst
        self.tag_str = tag_str
        self.request_url = request_url
        self.debug = debug
        self.done = False
    
    def toString(self):
        return f"{self.url} {self.dst} {self.tag_str} {self.debug}"

import imghdr
import http
'''
    downloader



'''
def downloader(queue, event, type = "img"):
    while True:
        logging.info(f"thread tick queue size {queue.qsize()} for type {type}")
        try:
            item:ItemDownload = queue.get()
        except Empty:
            continue
        else:
            # logging.info(f'work with {item}')
            url = item.url.encode('ascii', 'ignore').decode('ascii')
            out_file = item.dst            
            # logging.info(f'download {url} {out_file}')            
            import time
            time.sleep(1)
            try:                
                #urllib.request.urlretrieve(url2, out_file)
                request = urllib.request.Request(url, None, headers)
                image = urllib.request.urlopen(request, timeout=timeout).read()
                if not imghdr.what(None, image):
                    print('[Error]Invalid image, not saving {}'.format(url))
                    event.send(type, "error", out_file)
                    raise
                with open(out_file, 'wb') as f:
                    f.write(image)                    
                    item.done = True
                    event.send("data", "downloaded", item)
                    event.send(type, "downloaded", out_file)
                    
            except urllib.error.HTTPError as e:
                logging.error(f"error {out_file} {e}")
                event.send(type, "error", out_file)
            except urllib.error.URLError as e:
                logging.error(f"error {out_file} {e}")
                event.send(type, "error", out_file)
            except http.client.RemoteDisconnected as e:
                logging.error(f"error {out_file} {e}")
                event.send(type, "error", out_file)
            except UnicodeEncodeError as e:
                logging.error(f"error {out_file} {e}")
                event.send(type, "error", out_file)
            except Exception as e:
                logging.error(f"error {out_file} {e}")
                event.send(type, "error", out_file)
                
            if os.path.exists(out_file):
                if not imghdr.what(out_file):
                    os.remove(out_file)
                    event.send(type, "error", out_file)
            
            queue.task_done()
            
            if type == "word":
                if queue.qsize() == 0:
                    event.waiting_word = False
                    event.send(type, "finish")
            elif type == "trends":
                if queue.qsize() == 0:
                    event.send(type, "finish")            
            elif type == "img":
                if queue.qsize() == 0:
                    event.send("tags", "finish")





'''


UrlRetriever
retrieve urls list for tag
'''
class TagURLS():
    
    def __init__(self, tag_str:str, page: int = 0):
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        self.limit = cfg['app']['limit']
        self.tag_str = tag_str        
        self.page = page
    
    def retrieve(self, page):
        self.page = page
        adult = 'off'
        filters = ""
        request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.tag_str) \
                          + '&first=' + str(self.page * self.limit) + '&count=' + str(self.limit) \
                          + '&adlt=' + adult + '&qft=' + filters

        debug = f'TagURLS {str(self.page * self.limit)} - {str(self.limit)} - {request_url}'
        try:
            encoded_url = urllib.parse.quote(request_url, safe='/:?&=')
            request = urllib.request.Request(encoded_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)        
            html = response.read().decode('utf8')
            #html = response.read()
            self.links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
        except UnicodeEncodeError as e:
            print(e)
            return None
        
        return self.links, debug, request_url


'''


'''
class Images():
    
    def __init__(self, event):
        self.event = event
        self.buffer_size = 512
        
        self.queue = LifoQueue()
        self.started = False
        
        self.word_queue = LifoQueue()
        self.word_started = False

        self.trends_queue = LifoQueue()
        self.trends_started = False
        
    def start_thread(self):
        self.downloader_thread = Thread(
            target=downloader,
            args=(self.queue,self.event),
            daemon=True
        )
        self.downloader_thread.start()
        self.started = True        

    def start_word_thread(self):
        self.word_downloader_thread = Thread(
            target=downloader,
            args=(self.word_queue, self.event, "word"),
            daemon=True
        )
        self.word_downloader_thread.start()
        self.word_started = True
        
    def start_trends_thread(self):
        self.trends_downloader_thread = Thread(
            target=downloader,
            args=(self.trends_queue, self.event, "trends"),
            daemon=True
        )
        self.trends_downloader_thread.start()
        self.trends_started = True        