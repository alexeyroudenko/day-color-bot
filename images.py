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
    


def save_image(self, link, file_path):
    link2 = link.encode('ascii', 'ignore').decode('ascii')
    request = urllib.request.Request(link2, None, headers)
    image = urllib.request.urlopen(request, timeout=timeout).read()
    if not imghdr.what(None, image):
        print('[Error]Invalid image, not saving {}'.format(link2))
        raise
    with open(file_path, 'wb') as f:
        f.write(image)


import imghdr
import http
# '''
# downloader
# '''
def downloader(queue, event, type = "img"):
    while True:
        logging.info(f"thread tick queue size {queue.qsize()}")
        try:
            item = queue.get()
        except Empty:
            continue
        else:
            # logging.info(f'work with {item}')
            url = item[0].encode('ascii', 'ignore').decode('ascii')
            out_file = item[1]
            logging.info(f'download {url} {out_file}')            
            import time
            time.sleep(2)
            try:                
                #urllib.request.urlretrieve(url2, out_file)
                request = urllib.request.Request(url, None, headers)
                image = urllib.request.urlopen(request, timeout=timeout).read()
                if not imghdr.what(None, image):
                    print('[Error]Invalid image, not saving {}'.format(url))
                    raise
                with open(out_file, 'wb') as f:
                    f.write(image)                    
                    event.send(type, "downloaded", out_file)                
                    
            except urllib.error.HTTPError as e:
                logging.error(f"error {out_file} {e}")
            except urllib.error.URLError as e:
                logging.error(f"error {out_file} {e}")
            except http.client.RemoteDisconnected as e:
                logging.error(f"error {out_file} {e}")
            except UnicodeEncodeError as e:
                logging.error(f"error {out_file} {e}")
            except Exception as e:
                logging.error(f"error {out_file} {e}")
                
            if os.path.exists(out_file):
                if not imghdr.what(out_file):
                    os.remove(out_file)
            
            queue.task_done()
            if type == "word":
                if queue.qsize() == 0:
                    event.waiting_word = False
                    event.send(type, "finish")



headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
timeout = 1


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

        try:
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)        
            html = response.read().decode('utf8')
            #html = response.read()
            self.links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
        except UnicodeEncodeError as e:
            print(e)
            return None
        
        return self.links 


'''


'''
class Images():
    
    def __init__(self, event):
        self.event = event
        self.buffer_size = 512
        self.queue = LifoQueue()
        self.word_queue = LifoQueue()
        self.started = False
        self.word_started = False        
        
    def start_thread(self):
        # run download threds
        self.downloader_thread = Thread(
            target=downloader,
            args=(self.queue,self.event),
            daemon=True
        )
        self.downloader_thread.start()
        self.started = True        

    def start_word_thread(self):
        # run download words
        self.word_downloader_thread = Thread(
            target=downloader,
            args=(self.word_queue, self.event, "word"),
            daemon=True
        )
        self.word_downloader_thread.start()
        self.word_started = True