#!/home/pi/jamming_bot/.venv/bin/python
import os
import sys
from datetime import datetime
from urllib.parse import urlparse
from PIL import Image, ImageFilter
import logging, sys
import yaml
from yaml.loader import SafeLoader
from utils.collage_maker import make_collage
from PIL import Image, ImageFilter
import cv2
import numpy as np
from utils.colors import get_colours
from utils.som import get_som

from utils.bing import Bing
from utils.retrieve_twitter import retrieve_tags

import os
import shutil


def download(query, limit=100, output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60):
    # engine = 'bing'
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'
    cwd = os.getcwd()
    image_dir = os.path.join(cwd, output_dir)

    if force_replace:
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
    # check directory and create if necessary
    try:
        if not os.path.isdir("{}/{}/".format(cwd, output_dir)):
            os.makedirs("{}/{}/".format(cwd, output_dir))
    except:
        pass
    if not os.path.isdir("{}/{}".format(cwd, output_dir)):
        os.makedirs("{}/{}".format(cwd, output_dir))

    bing = Bing(query, limit, output_dir, adult, timeout)
    count = bing.run()
    return count

#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
def resizeImage(infile, outfile, size = 341):
    try :
        quality_val = 90
        im = Image.open(infile)
        im = im.resize(size=(size, size))
        #!im.thumbnail((341, 341), Image.ANTIALIAS)
        os.unlink(outfile)
        # gaussImage = im.filter(ImageFilter.GaussianBlur(4))
        # gaussImage.save(outfile, "JPEG")
        im.save(outfile, "JPEG")
        # print(im.size)
    except IOError:
        print("cannot reduce image")


def make_collages(filename_collage, count = 3):
        # get images
        files = [os.path.join("tmp", fn) for fn in os.listdir("tmp")]
        images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg', '.jpeg', '.png')]
        if not images:
            print('No images for making collage! Please select other directory with images!')
            exit(1)

        for file in images:
            resizeImage(file, file)
        print('start collage')
        res = make_collage(images, filename_collage, 1024, 1024, count)

def hextriplet(colortuple):
    return '#' + ''.join(f'{i:02X}' for i in colortuple)

def plot_colors2(center):
    size = 171
    bar = np.zeros((size * 3, size * 3, 3), dtype="uint8")
    i = 0
    for c in center:
        color = (int(c[0]), int(c[1]), int(c[2]))
        startX = (i % 3) * size
        endX = ((i % 3) + 1) * size
        cv2.rectangle(bar, (int(startX), int(i / 3) * size), (int(endX), (int(i / 3) + 1) * size), color, -1)
        i = i + 1

    return bar

def palette(infile, outfile):
    img = cv2.imread(infile)
    K = 9
    Z = img.reshape((-1,3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    for i, c in enumerate(np.uint8(center)):
        print(hextriplet(c))
    bar = plot_colors2(center);
    img = Image.fromarray(bar, 'RGB')
    img.save(outfile)

def download_img(trends, delete_prev = True, count_limit = 9):
    if delete_prev:
        list( map( os.unlink, (os.path.join( "tmp",f) for f in os.listdir("tmp")) ) )

    count = 0
    count_d = 0
    trends_text = ''
    for trend in trends:
        trends_text += "" + trend + "\n"
        query_string = trend
        count_downloaded = download(query_string, limit=count_limit,  output_dir='tmp', adult_filter_off=True, force_replace=True, timeout=60)
        count_d = count_d + count_downloaded
        count = count + 1
        if count_d >= count_limit:
            break
    return trends_text

'''
Python color bot.
Author: arthew0 (alexey.roudenko@gmail.com)
'''
class ColorBot():
    """Python color bot.
        Author: arthew0 (alexey.roudenko@gmail.com)
        TODO: add sites screenshots
    """
    def __init__(self, count = 4):
        self.phrase = "water"
        self.step_number = 0
        self.count = count
        self.is_active = True
        self.count_errors = 0

    """
    Controls
    """
    def start(self, phrase):
        self.phrase = phrase
        logging.info(f"start with {phrase}")
        self.step_number = 0
        
    def step(self):
        logging.debug(f"self.step {str(self.step_number)}")
        self.step_number = self.step_number + 1
        try:
            #download_img([self.phrase], True, self.count*self.count*self.count)
            download_img([self.phrase], True, 100)

        except Exception as e2:
            self.count_errors += 1
            logging.error(f"Exception step 2 {e2}")
            #print(f"Exception in step 2: {rows}", e, traceback.print_exc())
            if self.count_errors > 10:
                self.stop()
                exit()
            pass

    
    def make_collage(self):
        from pathvalidate import sanitize_filename
        import cyrtranslit
        file_base = cyrtranslit.to_latin(self.phrase, "ru")
        folder = "out/"
        filename_collage  = f"{folder}{file_base}_src.jpg"
        make_collages(filename_collage, self.count)
        pass

    def make_spot(self):
        folder = "out/"
        import cyrtranslit
        file_base = cyrtranslit.to_latin(self.phrase, "ru")
        filename_collage  = f"{folder}{file_base}_src.jpg"
        filename_palette  = folder + file_base + "_pal.png"
        filename_col      = folder + file_base + "_col.png"
        filename_som      = folder + file_base + "_som.png"
        filename_blr      = folder + file_base + "_blr.png"
        
        rgb_colours, hex_colors, colors = get_colours(filename_collage, 8, True, filename_palette)
        rgb_colours = rgb_colours[0:7]
        
        # -------------------------------------------------------------------------
        logging.debug("ret colors") 
        bar = plot_colors2(rgb_colours)
        img = Image.fromarray(bar, 'RGB')
        img.save(filename_col)

        np_colors = np.array(rgb_colours)
        raw_data_test = np_colors.T

        # -------------------------------------------------------------------------
        logging.debug("calc_som")
        get_som(raw_data_test, 1000, filename_som, 16)


        srciImage = Image.open(filename_som)
        gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
        gaussImage.save(filename_blr)
        return filename_blr


    def stop(self):
        pass

    def reset(self):
        pass



def main():
    config_file = "color_worker.yaml"
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    if config['color_log']:
        logger = logging.getLogger()
        import coloredlogs 
        coloredlogs.install(level="INFO", logger=logger)
        coloredlogs.install(fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s')

    bot = ColorBot(config['count'])
    bot.start(config['phrase'])
    bot.step()
    bot.make_collage()
    bot.make_spot()


if __name__ == '__main__':
    now = datetime.now()
    
    log_file_name = f"color_worker.log"
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        handlers=[
                            logging.FileHandler(log_file_name),
                            logging.StreamHandler(sys.stdout)
                        ],
                        # filemode='a',
                        encoding='utf-8',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    

    main()
