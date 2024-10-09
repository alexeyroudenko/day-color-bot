# from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file, render_template
from werkzeug.utils import secure_filename
import os

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
from PIL import Image

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

#Identify Colours
def get_img(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_colours(img_path, no_of_colours, show_chart, out_path):
    img = get_img(img_path)
    #Reduce image size to reduce the execution time
    mod_img = cv2.resize(img, (512, 512), interpolation = cv2.INTER_AREA)
    #Reduce the input to two dimensions for KMeans
    mod_img = mod_img.reshape(mod_img.shape[0]*mod_img.shape[1], 3)

    #Define the clusters
    clf = KMeans(n_clusters = no_of_colours)
    labels = clf.fit_predict(mod_img)

    counts = Counter(labels)
    counts = dict(sorted(counts.items()))

    center_colours = clf.cluster_centers_
    ordered_colours = [center_colours[i] for i in counts.keys()]
    hex_colours = [RGB2HEX(ordered_colours[i]) for i in counts.keys()]
    rgb_colours = [ordered_colours[i] for i in counts.keys()]

    if (show_chart):
        plt.figure(figsize = (8, 8))
        # plt.pie(counts.values(), labels = hex_colours, colors = hex_colours)
        plt.pie(counts.values(), labels = hex_colours, colors = hex_colours, radius = 512)
        plt.savefig(out_path, transparent=True)
        # os.remove(img_path)

        new_width = 512
        new_height = 512
        im = Image.open(out_path)
        width, height = im.size
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2
        im = im.crop((left, top, right, bottom))

        im.save(out_path)

        # print(rgb_colours)
        return rgb_colours, hex_colours, ordered_colours
    else:
        return rgb_colours


# files = [os.path.join("out", fn) for fn in os.listdir("out")]
# images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg')]
#
# for file in images:
#     if os.path.splitext(file)[1] == '.jpg':
#         out_path = os.path.splitext(file)[0]+'.png'
#         print(file);
#         print(out_path);
#         get_colours(file, 9, True, out_path)
