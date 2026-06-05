
# import click
import requests
import logging
import logging.handlers
logging.basicConfig(
    format="%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('spot')  

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
    


from PIL import Image, ImageFilter, ImageFile
  
'''
    Magic
'''  
def make_collages(images_paths, filename_collage):
    import math
    side_count = math.ceil(math.sqrt(len(images_paths)))
    #logging.info(f'side_count {side_count}')
    if not images_paths:
        print('No images for making collage! Please select other directory with images!')
        exit(1)

    w = int(1024/side_count)
    h = int(1024/side_count)
    size = int(w/side_count)
    collage_image = Image.new('RGB', (w, h), (35, 35, 35))
    for i, img_path in enumerate(images_paths[0:side_count*side_count]):            
        img = Image.open(img_path)        
        # img.resize((w,h))
        img.thumbnail((w,h))
        collage_image.paste(img, ((i % side_count) * size, int(i / side_count) * size))
    
    logging.info(f'save collage to {filename_collage}')
    collage_image.save(filename_collage)
    return filename_collage        

  
'''
    Magic
'''  
def make_collages_folder(folder_paths, filename_collage):
    import glob
    images_paths = glob.glob(folder_paths + "*")
    make_collages(images_paths, filename_collage)
  


import numpy as np
from colors.colors import get_colours
from colors.colors import plot_colors2
from colors.som import get_som 
'''
    Magic
'''  
def make_spot(collage_path, phrase, folder):
    import cyrtranslit
    file_base = cyrtranslit.to_latin(phrase, "ru")
    filename_palette  = folder + file_base + "_pal.png"
    filename_col      = folder + file_base + "_col.png"
    filename_som      = folder + file_base + "_som.png"
    filename_blr      = folder + file_base + "_blr.png"
    filename_info     = folder + file_base + ".txt"
    
    rgb_colours, hex_colors, colors = get_colours(collage_path, 10, True, filename_palette)
    rgb_colours = rgb_colours[0:7]
    
    f = open(filename_info, "w")
    for c in hex_colors:
        f.write("%s\n" % c)
    f.close()
    
    bar = plot_colors2(rgb_colours)
    img = Image.fromarray(bar, 'RGB')
    img.save(filename_col)

    np_colors = np.array(rgb_colours)
    raw_data_test = np_colors.T

    get_som(raw_data_test, 1000, filename_som, 16)

    srciImage = Image.open(filename_som)
    gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
    gaussImage.save(filename_blr)
    
    preceed_imgs = []
    preceed_imgs.append(collage_path)
    preceed_imgs.append(filename_palette)
    preceed_imgs.append(filename_col)
    preceed_imgs.append(filename_som)
    preceed_imgs.append(filename_blr)
    preceed_imgs.append(filename_info)
    return filename_blr, preceed_imgs

# def get_collage_path(query):
#     cfg['app']['tags_folder'] + f"{query}_src.jpg"
    
# '''
# Main
# '''
# @click.command()
# @click.option("--query", default="morning", help="Query")
# def make_spot_app(query:str) -> None:
#     collage_path = cfg['app']['tags_folder'] + f"{query}_src.jpg"
#     make_collages_folder(cfg['app']['tags_folder'] + f"/{query}/", collage_path)
#     spot_path = make_spot(collage_path, query, cfg['app']['spot_folder'])
# if __name__ == '__main__':
#     make_spot_app()
# from images import Images
 
 
from redis import Redis
redis = Redis(host='redis', port=6379)                
import pickle

def run(msg, type, tag, images):    
    if type == "tag":
        collage_path = cfg['app']['spot_folder'] + f"{tag}_src.jpg"
        
    if type == "combined":
        collage_path = cfg['app']['spot_folder']  + f"{tag}_src.jpg"
        
    
    logger.info(f"call make_collages collage_path")
    make_collages(images, collage_path)
    
    logger.info(f"call make_spot {str(tag)} {str(cfg['app']['spot_folder'])}")
    filename_blr, process_imgs = make_spot(collage_path, tag, str(cfg['app']['spot_folder']))

    
    # send
    import requests
    url = f'http://10.0.0.10:5000/spot/new/'
    form = {}
    form['type'] = type
    form['tag'] = tag
    form['query'] = tag
    form['src'] = process_imgs[0]
    form['pal'] = process_imgs[1]
    form['col'] = process_imgs[2]
    form['som'] = process_imgs[3]
    form['blr'] = process_imgs[4]
    form['txt'] = process_imgs[5]
    
    logger.info(f"call spot/new {str(url)} {str(form)}")
    
    requests.post(url, form)

def event_images_handler(msg):
    # calc
    #print(f"img event_images_handler {msg} -------------------- ")
    channel = msg['channel'].decode('utf-8')
    
    images = pickle.loads(msg['data'])
    print(images)
    image = images[0]
    print(image)
    tag = image.split('/')[-2:-1]
    print(tag)
    
    tag = str((images[0].split('/')[-2:-1])[0])
    print(f"img event_images_handler {channel} {images} tag:{tag}")    
    run(msg, "tag", tag, images)

def event_tag_handler(msg):
    channel = msg['channel'].decode('utf-8')
    data = str(msg['data'])
    print(f"event_tag_handler {data} no action")
    #images = pickle.loads(msg['data'])
    #print(f"img event_tag_handler {channel} {images} ----------------------- ")
    
def event_tag2_handler(msg):
    channel = msg['channel'].decode('utf-8')    
    images = pickle.loads(msg['data'])
    print(images)
    image = images[0]
    print(image)
    tags = image.split('/')[-2:-1]
    tag = str(tags[0])
    print(tag)

    #tag = str(images[0].split('/')[-2:-1])[0]    
    print(f"img event_tag2_handler {channel} {images} tag:{tag}")
    run(msg, "tag", tag, images)
    
def event_combined_handler(msg):
    #print(f"img event_tag_handler {msg}")
    # channel = msg['channel'].decode('utf-8')
    # data = msg['data']
    # print(f"img {channel} {data}")
    images = pickle.loads(msg['data'])
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    now_sec = datetime.datetime.now().strftime('%Y-%m-%d-%H-%m-%s')
    print(f"img event_combined_handler {now} make combined collage at {now_sec}")
    run(msg, "combined", now, images)

import time
if __name__ == '__main__':
    
    print("start spot 2.0.1")

    pubsub = redis.pubsub()
    pubsub.psubscribe(**{"images": event_images_handler})
    pubsub.psubscribe(**{"tag_add": event_tag_handler})    
    
    pubsub.psubscribe(**{"tag2_images": event_tag2_handler})        
    pubsub.psubscribe(**{"combined_mages": event_combined_handler})    
    
    pubsub.run_in_thread(sleep_time=0.01)