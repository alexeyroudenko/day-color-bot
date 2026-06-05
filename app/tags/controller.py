import os

import requests
from tags import Tag
from tags import State
from tags import save_trends

from events import Event

# from images import TagURLS
# from images import ItemDownload


import logging
logger = logging.getLogger('tags')

# import logging.handlers
# logging.basicConfig(
# 	format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
# 	level=logging.INFO,
# )
  

            
# '''

# '''
# from images import Images
from events import Observer
# from events import OSCsender
from redis import Redis

class Runner():    
    def __init__(self):
        self.spot_path = ""		
        self.redis = Redis(host='redis', port=6379)        
        
        self.event = Event()
        self.state = State(self.event)        
        self.observer = Observer(self.event)        
        
        self.observer.attach(self)        

    '''
        Listen Event Class events
        convert events to commands
    '''
    def on_event(self, args):
        logger.info(f"Runner on_event {args}")
        msg = args[0]
                
        # tags events    
        if msg == "tag":
            action = args[1]
            tag_str = args[2]            
            self.redis.publish(f"tag_{action}", tag_str)
            
            url = f'http://10.0.0.10:5000/tag/tag_{action}/{tag_str}/'
            logger.info(url)
            r = requests.get(url)
            # print(f"{r}")

    '''
        Regular logic
    '''
    def step(self, trends):
        #self.event.send("trends", "process_trends", trends)
        self.event.send("msg", "process_trends", trends)
        self.state.update(trends)
        self.state.save()
  
        import pickle
        self.redis.set("trends", pickle.dumps(list(self.state.dump())))
        logger.info(f"save trends to redis")
        
        

    '''
        Retrieve word from TG
    '''
    # def process_msg_thread(self, *args):
    # 	logger.info(f"process_msg {args}")
    # 	# word = args[0]
    # 	# self.event.send("msg", "process_msg", word)		
    # 	# folder = cfg['app']['tags_folder'] + word + "/"
    # 	# os.makedirs(folder, exist_ok=True)
    # 	# command = AddToQueueWordCommand(self.images)
    # 	# command.execute(word)
    # 	# self.word_command = command
    # 	# self.event.waiting_word = True
    # 	# self.event.waiting_word_spot = True
        
    # '''
    # 	Retrieve word from TG
    # '''

    # def process_msg(self, *args):      
    # 	self.process_msg_thread(args[0])
    # 	import time
    # 	while self.event.waiting_word == True:
    # 		time.sleep(0.5)
    # 	while self.event.waiting_word_spot == True:
    # 		time.sleep(0.5)
    # 	return self.spot_path