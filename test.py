from tags import retrieve_trends
from tags import Runner 
import logging
import logging.handlers

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')  

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)

import time
if __name__ == '__main__':

    logic = 0
    run = Runner()
        
    # logger.info("process_msg")
    # run.process_msg("color")
    # time.sleep(10)
    # trends = retrieve_trends()
    # run.loop(trends)
    # time.sleep(10)
    # time.sleep(5)
    # logger.info("tag1 reuse tafs")
    
    run.loop(["tag1"])
    time.sleep(15)
    run.loop(["tag2"])
    time.sleep(15)
    run.loop(["tag3"])    
    time.sleep(15)
    run.loop(["tag1", "tag2", "tag3"])    
    
    print("finish")