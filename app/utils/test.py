from tags import retrieve_trends
from controller import Runner 
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


from redis import Redis
redis = Redis(host='redis', port=6379)


import time
if __name__ == '__main__':
    logic = 0
    runner = Runner()
    while True:
        
    # logger.info("process_msg")
    # run.process_msg("color")
    # time.sleep(10)
    # trends = retrieve_trends()
    # run.loop(trends)
    # time.sleep(10)
    # time.sleep(5)
    # logger.info("tag1 reuse tafs")
    
        # spot_path = runer.process_msg("color")
        # print(spot_path)
        # time.sleep(20)
        # while runer.event.waiting_word == True:
        #     time.sleep(0.5)
        # while runer.event.waiting_word_spot == True:
        #     time.sleep(0.5)
            
        #time.sleep(60)
    
        import pickle
        pickle.dumps(list(runner.state.dump()))
        
        runner.loop(["tag1"])
        redis.set("trends", pickle.dumps(list(runner.state.dump())))
        time.sleep(20)
        runner.loop(["tag2"])
        redis.set("trends", pickle.dumps(list(runner.state.dump())))
        time.sleep(20)
        runner.loop(["tag3"])
        redis.set("trends", pickle.dumps(list(runner.state.dump())))
        time.sleep(20)
        runner.loop(["tag1", "tag2", "tag3"])        
        redis.set("trends", pickle.dumps(list(runner.state.dump())))
        
        redis.publish('trends', pickle.dumps(list(runner.state.dump())))
    
    print("finish")