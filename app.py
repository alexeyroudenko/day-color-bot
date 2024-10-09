from tags import retrieve_trends
from tags import Runner 
import logging
import logging.handlers

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')     

if __name__ == '__main__':
    logic = 0
    run = Runner()
    while True:
        
        if logic % 20 == 19:
            run.process_msg("summer")   

        if logic % 5 == 4:
            trends = retrieve_trends()[0:cfg['app']['count_trends']]
            run.loop(trends)                            
            logger.info(f"trends {trends}")
                        
        logic += 1
        logger.info(f"sleep")    
        import time
        time.sleep(60*5)