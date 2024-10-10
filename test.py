from tags import retrieve_trends
from tags import Runner 

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)

import time
if __name__ == '__main__':

    logic = 0
    run = Runner()
        
    run.process_msg("color")
    
    time.sleep(10)
    
    trends = retrieve_trends()
    run.loop(trends)
    
    time.sleep(10)
    
    print("finish")