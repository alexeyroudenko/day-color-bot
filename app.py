from tags import retrieve_trends
from tags import Runner 

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)


if __name__ == '__main__':
    logic = 0
    run = Runner()
    while True:
        
        # if logic % 20 == 19:
        #     run.process_msg("summer")   

        if logic % 5 == 0:
            # trends = retrieve_trends()[0:cfg['app']['count_trends']]
            # run.loop(trends)
            run.loop(['sleep_time', 'sleep_hours'])
                        
        logic += 1
        import time
        time.sleep(60*5)