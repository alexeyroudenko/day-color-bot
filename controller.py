import os
from tags import Tag
from tags import State
from events import Event
from images import TagURLS
from tags import save_trends
import logging
import logging.handlers
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')  

from images import ItemDownload

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
    
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
        from spot import make_collages_folder
        from spot import make_spot
        collage_path = cfg['app']['spot_folder'] + f"{word}_src.jpg"
        make_collages_folder(cfg['app']['tags_folder'] + f"/{word}/", collage_path)
        spot_path = make_spot(collage_path, word, cfg['app']['spot_folder'])
        return spot_path
        
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
        self.spot_path = ""
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
                if cfg['app']['restart_collect'] == True:
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
                self.spot_path = command.execute(word)
                self.event.waiting_word_spot = False

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
        self.event.waiting_word_spot = True