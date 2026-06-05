"""
File: img.py
Author: Alexey Roudenko
Description: listen tags event via reddis and add to download queue
"""
import os
from images import ItemDownload 
from images import TagURLS
from images import Images

import logging
logger = logging.getLogger('img')  

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)


import pickle
import re
import imghdr
import http
import time
import urllib.error
import urllib.request
headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
timeout = 1



from redis import Redis
redis = Redis(host='redis', port=6379) 

import glob
from queue import Empty, Queue, LifoQueue

'''


'''
class TagDownloader():
    def __init__(self, tag_str: str):
        self.tag_str = tag_str
        self.tag_urls = TagURLS(str(tag_str), 0, cfg['app']['limit']) 
        self.queue = LifoQueue()
        self.current_url = 0
        self.current_imt = 0
        self.page = 0
        self.error = False
        self.urls = []

    def hasSpotImage(self):
        filepath = os.path.abspath(f"data/spot/{self.tag_str}.txt")        
        has = os.path.isfile(filepath)
        if not has:
            open(filepath, 'a').close()            
        print(f"------ check hasspot {has}")
        return has
    

    def getPathImages(self):
        #cfg['app']['tags_folder']
        return os.path.abspath(f"data/tags/{self.tag_str}/") + "/"
        
    def getCountImages(self):
        return len(glob.glob(self.getPathImages() + '/*'))
    
    def getDownloadedPaths(self):
        return glob.glob(self.getPathImages() + '/*')
    
    def download(self, count):
        downloaded = []
        #logging.info(f'work count in folder {self.getPathImages()} {self.getCountImages()} but need {count}')
        os.makedirs(self.getPathImages(), exist_ok=True)
        while self.getCountImages() < count and self.error == False:
            #print(f"self.current_url : {self.current_url }")
            self.current_img = self.getCountImages()
            logging.info(f'work count in folder {self.getPathImages()} {self.getCountImages()} but need {count} {len(self.urls)}')
            
            if len(self.urls) == 0 or len(self.urls) <= self.current_url:
                urls_, debug_, request_url_ = self.tag_urls.retrieve(self.page)
                #print(f"urls_: {urls_}")
                for url in urls_:
                    self.urls.append(url)
                    logging.info(f"added {url}")
                logging.info(f"fetched {len(urls_)} urls in page {self.page}")

                if len(urls_) == 0:
                    self.error = True
                    logging.error(f"fetched zero url")
                    break
                else:
                    self.page += 1
                    self.current_url = 0
            
            logger.info(f"len urls {len(self.urls)} {self.current_url}")
            img_url = self.urls[self.current_url]            
            out_file = self.getPathImages() + f"{self.current_img}.jpg"
            item = ItemDownload(img_url, out_file, self.tag_str, "request_url", "debug")
            if self.download_action(item):
                downloaded.append(item)
            self.current_url += 1
        
                
            
        # if len(downloaded) > 0:
        #     paths = self.getDownloadedPaths()
        #     logger.info(f"downloaded {len(paths)}")
        #     redis.publish(f"images", pickle.dumps(paths))
            

            
    def download_action(self, item:ItemDownload):
        # logging.info(f'work with {item}')
        url = item.url.encode('ascii', 'ignore').decode('ascii')
        out_file = item.dst
        
        try: 
            request = urllib.request.Request(url, None, headers)
            image = urllib.request.urlopen(request, timeout=timeout).read()
            #import time
            #time.sleep(4)
            if not imghdr.what(None, image):
                print('[Error]Invalid image, not saving {}'.format(url))
                raise
            with open(out_file, 'wb') as f:                    
                f.write(image)                    
                logging.info(f"ok {out_file}")
                out_file = out_file
                
                
                import requests
                url = f'http://10.0.0.10:5000/img/new/'
                data = {}
                data['path'] = out_file
                data['tag'] = item.tag_str
                logger.info(url, data)
                r = requests.post(url, data)
                # print(f"{r}")
                
                # TODO: Check img file
                # self.current+=1
        except:
            logging.error(f"error download_action {out_file}")
            return None
            
        if os.path.exists(out_file):
            if not imghdr.what(out_file):
                os.remove(out_file)
                return None

        return True
        
    
    def load(self):
        ...
        
    def update(self):
        ...


'''


'''
class Pool():
    def __init__(self):
        self.data = {}    
        
    def update(self, tag_str):
        if tag_str not in self.data.keys():
            tag = TagDownloader(tag_str)
            self.data[tag_str] = tag
            tag.load()
            tag.update()
        else:
            tag = self.data[tag_str]
            tag.update()
                
    def delete(self, tag_str):
        if tag_str in self.data.keys():
            # tag = self.data[tag_str]
            # tag.save()
            del self.data[tag_str]
                                

class PoolController():
    def __init__(self):
        self.pool = Pool()
        
    def update(self, tag_str):
        self.pool.update(tag_str)
        
    def delete(self, tag_str):
        self.pool.delete(tag_str)

    def clear(self):
        while len(self.pool.data.keys())>0:
            key = self.pool.data.keys()[0:0]
            del self.data[key]
        

'''


'''
class DayController():
    def __init__(self, pool: Pool):
        self.pool = pool
        
    def run(self):
        for item in self.pool.data.items():
            itt = TagDownloader(item[0]).download(cfg['app']['limit'])
    
    #
    # Check mix current state spot                
    def ckeck_mix_spot(self):
        tags_strs = self.pool.data.keys()
        logger.info("check enought images for MIX SPOT {tags_strs} hasPot:{hasSpot}")
        combined_paths = [] 
        import datetime
        date_tag = datetime.datetime.now().strftime('%Y-%m-%d-%H')
        hasSpot = TagDownloader(date_tag).hasSpotImage()            
        if not hasSpot:
            for tag in tags_strs:
                if TagDownloader(tag).getCountImages() > 0:
                    path = TagDownloader(tag).getDownloadedPaths()[0]
                    combined_paths.append(path)
            if len(combined_paths):
                logger.info(f"see combined_mages for MIX SPOT combined_paths:{len(combined_paths)}")
                redis.publish(f"combined_mages", pickle.dumps(combined_paths))

    #
    # Check tag spot        
    def check_tag_spot(self):
        tags_strs = self.pool.data.keys()
        logger.info("check enought images for TAG SPOT")
        tagg_paths = []
        for tag in tags_strs:
            hasSpot = TagDownloader(tag).hasSpotImage()            
            imgs = TagDownloader(tag).getDownloadedPaths()
            hasCount = len(imgs) == cfg['img']['count_for_spot']                        
            logger.info(f"check TAG SPOT {len(imgs)} {cfg['img']['count_for_spot']} = {hasCount} hasPot:{hasSpot}")
            if hasSpot == False and hasCount == True:
                # send to spot
                logger.info("see tag2_images for TAG SPOT")
                redis.publish(f"tag2_images", pickle.dumps(imgs))
            else: 
                # send to spot
                logger.info("not for TAG SPOT")
                
            #print(TagDownloader(item).tag_urls.retrieve)
            #TagDownloader(item).tag_urls.retrieve
                              
    def ckeck_spot(self):        
        
        self.ckeck_mix_spot()
        
        self.check_tag_spot()
        
        
    # def update(self, tag_str):
    #     self.pool.update(tag_str)        
    # def delete(self, tag_str):
    #     self.pool.delete(tag_str)
        
        
# from images import Images
from events import Event
from events import Observer


class Runner():    
    def __init__(self):
        self.poolController = PoolController()
        self.dayController = DayController(self.poolController.pool)
  
        self.spot_path = ""
        self.started = False		
        self.redis = Redis(host='redis', port=6379)        		
        self.event = Event()
        self.observer = Observer(self.event)
        self.observer.attach(self)
        self.images = Images(self.event)

    '''
        Listen Event Class events
        convert events to commands
    '''
    def on_event(self, args):
        logger.info(f"Runner on_event {args}")
        msg = args[0]

        # Extendet info for items
        if msg == "data":
            action = args[1]
            if action == "downloaded":
                data: ItemDownload = args[2]
                # print(f"cotroller {data}")                
                print(f"{action}	{data.toString()}")                
                # event.send(type, "downloaded", out_file)
                # print(f"data: {data}")
                



    
   


runner = Runner()

'''
    msg.channel 
    msg.data
'''

def event_day_handler(day):
    logging.info(f"img event_day_handler {day}")
    runner.dayController.ckeck_spot()
    
def event_trends_handler(msg):
    logging.info(f"img event_trends_handler {msg}")

def event_http_handler(msg):
    logging.info(f"img event_http_handler {msg}")

def event_tags_restart_handler(msg):
    logging.info(f"img event_tags_restart_handler {msg}")
    runner.poolController.clear()
    
def event_tag_handler(msg):
    logging.info(f"img event_tag_handler {msg}")
    # tags events    
    channel = msg['channel'].decode('utf-8')
    data = msg['data'].decode('utf-8')
    #print(channel, data)

    if channel == "tag_add" or channel == "tag_update":
        tag_str = data
        runner.poolController.update(tag_str)
        runner.dayController.run()
        runner.dayController.ckeck_spot()
        

        # logger.info(f"update tag {tag_str}")
        # command = AddToQueueCommand(runner.images)
        # command.execute(tag_str)
    
    if channel == "tag_delete":
        tag_str = data
        runner.poolController.delete(tag_str)


import time
if __name__ == '__main__':
    
    print("start img 2.0.0")

    pubsub = redis.pubsub()
    pubsub.psubscribe(**{"http": event_http_handler})
    pubsub.psubscribe(**{"trends": event_trends_handler})
    pubsub.psubscribe(**{"tag_add": event_tag_handler})
    pubsub.psubscribe(**{"tags_restart": event_tags_restart_handler})
    pubsub.psubscribe(**{"tag_update": event_tag_handler})
    pubsub.psubscribe(**{"tag_delete": event_tag_handler})
    pubsub.psubscribe(**{"day": event_day_handler})
    pubsub.run_in_thread(sleep_time=0.01)
    # while True:
        
    #     runner.poolController.update("summer")        
    #     runner.dayController.run()
        
    #     time.sleep(5)
        
    #     runner.poolController.update("winter")        
    #     runner.dayController.run()

    #     time.sleep(5)
        
    #     runner.poolController.update("tag3")        
    #     runner.dayController.run()
        
    #     time.sleep(5)
        
    #     runner.poolController.update("tag3")        
    #     runner.dayController.run()

    #     time.sleep(5)
        
  