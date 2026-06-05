# import tweepy
import os
import glob
import pathlib

import urllib
import utils.downloader as downloader
from utils.collage_maker import make_collage
from PIL import Image, ImageFilter
import cv2
import numpy as np
import webcolors
import time
import datetime
from utils.colors import get_colours
from utils.som import get_som
from utils.retrieve_twitter import retrieve_tags
 



#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
def retrieve_trends(woeid):
    tags = retrieve_tags()
    trends = tags[0:12]
    return trends

#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
def download_img(trends, delete_prev = True, count_limit = 9):
    if delete_prev:
        list( map( os.unlink, (os.path.join( "tmp",f) for f in os.listdir("tmp")) ) )

    count = 0
    count_d = 0
    trends_text = ''
    global_polarity = 0
    for trend in trends:
        #for trend in value['trends']:
        trends_text += "" + trend + "\n"
        text = trend
        query_string = trend
        # print("download %i" % count)
        count_downloaded = downloader.download(query_string, limit=1,  output_dir='tmp', adult_filter_off=True, force_replace=False, timeout=5)
        count_d = count_d + count_downloaded
        # print("count_downloaded:")
        # print(count_downloaded)

        count = count + 1
        if count_d >= count_limit:
            break
    return trends_text
    # print('Tags:')
    # print(trends_text)

#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
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
        im.save(outfile, "JPEG")
        print(im.size)
    except IOError:
        print("cannot reduce image")

#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
def make_collages(filename_collage):
        # get images
        files = [os.path.join("tmp", fn) for fn in os.listdir("tmp")]
        images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg', '.jpeg', '.png')]
        if not images:
            print('No images for making collage! Please select other directory with images!')
            exit(1)

        for file in images:
            resizeImage(file, file)

            # im = Image.open(image)
            # im.thumbnail(size)
            # im.save("thumbnail_%s_%s" % (image, "_".join(size)))

        # for file in images:
        #     resizeImage(file, file)
        #     palette(file, file + "_palette.jpg")
        # import random
        # random.shuffle(images)
        print('start collage')
        print(filename_collage)

        res = make_collage(images, filename_collage, 1024, 1024)
        # resizeImage(filename_collage, filename_collage, 1024)

#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
def main():


    while True:
        try:
            # SETUP -------------------------------------------------------------------
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)

            file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')
            folder = "out/"
            # file_base = "0"

            filename_textout  = folder + file_base + ".txt"
            filename_collage  = folder + file_base + "_src.jpg"
            filename_palette  = folder + file_base + "_pal.png"
            filename_col      = folder + file_base + "_col.png"
            filename_som      = folder + file_base + "_som.png"
            filename_blr      = folder + file_base + "_blr.png"


            place = "world"
            woeid = 1


            print("get trands")
            trends = retrieve_trends(woeid)

            print(f"trends {trends}")
            trends_text = download_img(trends)

            f = open(filename_textout, "w",  encoding="utf8")
            f.write("%s\n\n" % place)
            f.write("%s\n\n" % trends_text)
            f.close()

            # -------------------------------------------------------------------------
            print("make collage")
            make_collages(filename_collage)

            rgb_colours, hex_colors, colors = get_colours(filename_collage, 8, True, filename_palette)
            rgb_colours = rgb_colours[0:7]

            # -------------------------------------------------------------------------
            print("ret colors") 
            bar = plot_colors2(rgb_colours)
            img = Image.fromarray(bar, 'RGB')
            img.save(filename_col)

            np_colors = np.array(rgb_colours)
            raw_data_test = np_colors.T

            # -------------------------------------------------------------------------
            print("calc_som")
            get_som(raw_data_test, 1000, filename_som, 16)


            srciImage = Image.open(filename_som)
            gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
            gaussImage.save(filename_blr)


            f = open(filename_textout, "a")
            for c in hex_colors:
                f.write("%s\n" % c)
            f.close()

            # -------------------------------------------------------------------------
            print(f"finish >>> {filename_blr}")
            print("sleep 15 min")
            
            time.sleep(60*15)
        
        except Exception as inst:

            time.sleep(60*15)
            
            print(type(inst))    # the exception type
            print(inst.args)     # arguments stored in .args
            print(inst) 


if __name__ == "__main__":
    main()
