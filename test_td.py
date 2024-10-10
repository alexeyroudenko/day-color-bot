
import os
import time
from events import Event  
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
       

from images import Images
from events import Observer
from events import OSCsender
from images import ItemDownload
'''
Main
'''
def main():

    event = Event()    
    observer = Observer(event)
    osc = OSCsender()
    observer.attach(osc)

    while True:
        logging.info("---------------------------------------")            
        

        #trends = retrieve_trends()[0:cfg['app']['count_trends']]
        #logging.info(f"trends {trends}")             
        #run.loop(trends)        
        #logging.info(f"start sleep {cfg['app']['sleep_time']}")       
        #time.sleep(cfg['app']['sleep_time'])
        
        # import glob
        # files = glob.glob(cfg['app']['tags_folder'] + "*")        
        # tag_folder = files[event.count % len(files)]         
        # tag = os.path.basename(tag_folder)
        # event.send("tag", "add", tag)
        # time.sleep(60.0)

        # fast load images to TD
        import glob
        files = glob.glob("Z:\\Developer\\day-color-bot-airflow\\data\\out\\*_src*")
        path = files[event.count % len(files)]        
        item = ItemDownload("", path, "", "", "")
        # event.send("img", "downloaded" , files[event.count % len(files)])
        event.send("data", "downloaded" , item, path)
        time.sleep(0.1)
        
              
        # if event.count % 5 == 0:
        #     event.send("tag", "add" ,"winter")
        # elif event.count % 5 == 4:
        #     event.send("tag", "delete" ,"winter")
        # else:
        #     event.send("tag", "update" ,"winter")            
        # time.sleep(0.2)
                        
        # event.send("msg", "process_msg" ,"winter")
        # time.sleep(1)
        
if __name__ == '__main__':
    main()        