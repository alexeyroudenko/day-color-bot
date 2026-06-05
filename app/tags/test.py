from tags import retrieve_trends
from controller import Runner 


import logging
import logging.handlers
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')  



        
    # logger.info("process_msg")
    # run.process_msg("color")
    # time.sleep(10

        # trends = retrieve_trends()
        # runner.step(trends)
        # time.sleep(450)
        # redis.incr('tag_updates')
        # logger.info(f"tags update {redis.get('tag_updates')}")

  
        # tags = ["#GHGala7",
        # 	"#يحيي_السنوار",
        # 	"Corinthians",
        # 	"#TUDUMNaLata",
        # 	"Sinwar",
        # 	"#花より男子",
        # 	"集英社秋マンガチャ開催",
        # 	"#LINEマンガガチャ",
        # 	"対象作品",
        # 	"Hamas"]
        
          #runner.step(["#baystars", "#FGO", "#malatya", "たかほ", "カズラドロップ", "バーニス", "バーニス", "バーニス", "増田大輝", "バーニス"])
        #time.sleep(300)
  
    # time.sleep(5)
    # logger.info("tag1 reuse tafs")
    
        # spot_path = runer.process_msg("color")
        # print(spot_path)
        # time.sleep(20)
        # while runer.event.waiting_word == True:
        #     time.sleep(0.5)
        # while runer.event.waiting_word_spot == True:
        #     time.sleep(0.5)
             
        # #time.sleep(60)
        # import gevent	
        # gevent.sleep(5)
        # runner.redis.publish("trends")
        # runner.step(["tag1"])
        # gevent.sleep(5)
        # runner.step(["tag2"])
        # gevent.sleep(5)
        # runner.step(["tag3"])
        # gevent.sleep(5)
        # runner.step(["tag1", "tag2", "tag3"])        
        # gevent.sleep(5)
    
 
    

import requests

from redis import Redis
redis = Redis(host='redis', port=6379)
redis.set('tag_updates', 0)

# import os
# if os.isfile('text.txt'):
#     f = open('text.txt')
#     texts = f.read()
#     words = texts.replace("\n", " ").replace(",", " ").split(' ')
# else:

words = ['Spring', 'Summer', 'Autumn', 'Winter', 'Blossom', 'Harvest', 'Rain', 
            'Sunset', 'Forest', 'Frost', 'Meadow', 'Beach', 'Storm', 'Fog', 'Snow', 'Leaf', 'Petal', 'Sky',
            'Ocean', 'Dawn', 'Dusk', 'Thunder', 'Ice', 'Pebble', 'Sunflower', 'Pine', 'Maple', 'Cherry', 'Wheat', 'Berry', 'Cloud', 'Shadow', 'Stream', 'River', 
            'Desert', 'Jungle', 'Valley', 'Hill', 'Peak', 'Marsh', 'Blossom', 'Orchard', 'Rainforest', 'Tundra', 'Glade', 'Cove', 'Prairie', 'Bay', 'Cascade', 
            'Geyser', 'Lagoon', 'Oasis', 'Field', 'Canyon', 'Wetland', 'Coral', 'Ridge', 'Cliff', 'Grove', 'Marshland', 'Crater', 'Plateau', 'Archipelago', 
            'Savannah', 'Basin', 'Dune', 'Reef', 'Treetop', 'Thicket', 'Cactus', 'Slope', 'Springs', 'Gully', 'Vale', 'Heath', 'Meadowland', 'Seashore', 
            'Quagmire', 'Crag', 'Basin', 'Dingle', 'Dike', 'Knoll', 'Wetland', 'Bough', 'Boughs', 'Canopy', 'Highlands', 'Rivulet', 'Fen', 'Cove', 'Estuary', 'Hammock', 'Glade', 
            'Backwater', 'Shoreline', 'Cove', 'Harbor', 'Knoll', 'Cliffside', 'Highlands', 'Glimmer', 'Wisp', 'Cleft', 'Bayou', 'Hollow', 'Cove', 'Dell', 'Byway']

# for w in words:
#     if len(w) > 4:
#         song_words.append(w)        
        # for word in song_words:
        # 	print(f"add {word}")
        # 	url = f"http://localhost:5000/app_ctrl/add_word/{word}/"
        # 	requests.get(url)
        # 	time.sleep(20)
            
            
            
            
print("start tags 1.1.0") 
            
import time 
import random
random.shuffle(words)
if __name__ == '__main__':
    
    
    #r = requests.get(f'http://10.0.0.10:5000/tags/restart')
    redis.publish(f"tags_restart", "tags_restart")    
        
    counter = 0 
    runner = Runner()
    
    time.sleep(5)
    
    # print("start switch words")
    while True:
        
        import yaml
        with open('config.yml', 'r') as file:
            cfg = yaml.safe_load(file)

        if not cfg['trends']['simulate']:
            trends = retrieve_trends()
            runner.step(trends)
            logger.info(f"sleep {cfg['trends']['sleep_time']}")
            time.sleep(cfg['trends']['sleep_time'])
            redis.incr('tag_updates')
            logger.info(f"tags update {redis.get('tag_updates')}")
        
        else:
            
            trends = words[0:cfg['trends']['count']]
            if counter % 2 == 0:
                new_word = words[(counter + 1 + len(trends)) % len(words)]
                old_word =  trends[(counter + len(trends)) % len(trends)]                
                logger.info(f"changing {old_word} > {new_word}")
                trends[7 * counter % len(trends)] = new_word
                    
            runner.step(trends)
            logger.info(f"sleep {cfg['trends']['test_sleep_time']}")
            time.sleep(cfg['trends']['test_sleep_time'])
            redis.incr('tags_fetch_runs')
            counter+=1
 
#     # print("finish")