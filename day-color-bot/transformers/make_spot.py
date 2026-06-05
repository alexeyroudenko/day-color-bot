from __future__ import division
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches as patches
from PIL import Image
from werkzeug.utils import secure_filename
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







# 8 colours as initial test set
raw_data_test = np.array([[1, 0, 0], [0, 1, 0],
                [0, 0.5, 0.25], [0, 0, 1],
                [0, 0, 0.5], [1, 1, 0.2],
                [1, 0.4, 0.25], [1, 0, 1]]).T * 255

def crop_photo(file):

    new_width = 512
    new_height = 512

    im = Image.open(file)
    width, height = im.size
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2
    im = im.crop((left, top, right, bottom))

    im.save(file)


def get_som(raw_data, n_iterations, out_path, size=7, every = 0):

    # every = 10000

    # or use random colours
    # raw_data = np.random.randint(0, 255, (3, 100))
    # print(raw_data)

    # network_dimensions = np.array([5, 5])
    network_dimensions = np.array([size, size])

    # n_iterations = 100
    # n_iterations = 10000
    # init_learning_rate = 0.01

    init_learning_rate = 0.03


    normalise_data = True

    # if True, assume all data on common scale
    # if False, normalise to [0 1] range along each column
    normalise_by_column = False


    # establish variables based on data
    m = raw_data.shape[0]
    n = raw_data.shape[1]

    # initial neighbourhood radius
    init_radius = max(network_dimensions[0], network_dimensions[1]) / 2
    # radius decay parameter
    time_constant = n_iterations / np.log(init_radius)

    data = raw_data
    # check if data needs to be normalised
    if normalise_data:
        if normalise_by_column:
            # normalise along each column
            col_maxes = raw_data.max(axis=0)
            data = raw_data / col_maxes[np.newaxis, :]
        else:
            # normalise entire dataset
            data = raw_data / data.max()

    # setup random weights between 0 and 1
    # weight matrix needs to be one m-dimensional vector for each neuron in the SOM
    net = np.random.random((network_dimensions[0], network_dimensions[1], m))

    def find_bmu(t, net, m):
        """
            Find the best matching unit for a given vector, t, in the SOM
            Returns: a (bmu, bmu_idx) tuple where bmu is the high-dimensional BMU
                     and bmu_idx is the index of this vector in the SOM
        """
        bmu_idx = np.array([0, 0])
        # set the initial minimum distance to a huge number
        min_dist = np.iinfo(np.int_).max
        # calculate the high-dimensional distance between each neuron and the input
        for x in range(net.shape[0]):
            for y in range(net.shape[1]):
                w = net[x, y, :].reshape(m, 1)
                # don't bother with actual Euclidean distance, to avoid expensive sqrt operation
                sq_dist = np.sum((w - t) ** 2)
                if sq_dist < min_dist:
                    min_dist = sq_dist
                    bmu_idx = np.array([x, y])
        # get vector corresponding to bmu_idx
        bmu = net[bmu_idx[0], bmu_idx[1], :].reshape(m, 1)
        # return the (bmu, bmu_idx) tuple
        return (bmu, bmu_idx)
    def decay_radius(initial_radius, i, time_constant):
        return initial_radius * np.exp(-i / time_constant)

    def decay_learning_rate(initial_learning_rate, i, n_iterations):
        return initial_learning_rate * np.exp(-i / n_iterations)

    def calculate_influence(distance, radius):
        return np.exp(-distance / (2* (radius**2)))



    # every = 100

    for i in range(n_iterations):
        #print('Iteration %d' % i)
        if every > 0:
            if i % every == 0:
                print('Iteration %d' % i)
                fig = plt.figure()
                # setup axes
                ax = fig.add_subplot(111, aspect='equal')
                ax.set_xlim((0, net.shape[0]+1))
                ax.set_ylim((0, net.shape[1]+1))
                ax.set_title('Self-Organising Map after %d iterations' % n_iterations)

                # plot the rectangles
                for x in range(1, net.shape[0] + 1):
                    for y in range(1, net.shape[1] + 1):
                        ax.add_patch(patches.Rectangle((x-0.5, y-0.5), 1, 1,
                                     facecolor=net[x-1,y-1,:],
                                     edgecolor='none'))

                # plt.set_size_inches(8, 8)
                # filaname = "{}_{}_.png".format(out_path, i)
                filaname = "out/0/0_sop_%i_%04d.png" % (size, i)
                # print(filaname)
                plt.savefig(filaname, transparent=True, dpi=180)
                plt.close('all')
                crop_photo(filaname)


        # select a training example at random
        t = data[:, np.random.randint(0, n)].reshape(np.array([m, 1]))

        # find its Best Matching Unit
        bmu, bmu_idx = find_bmu(t, net, m)

        # decay the SOM parameters
        r = decay_radius(init_radius, i, time_constant)
        l = decay_learning_rate(init_learning_rate, i, n_iterations)

        # now we know the BMU, update its weight vector to move closer to input
        # and move its neighbours in 2-D space closer
        # by a factor proportional to their 2-D distance from the BMU
        for x in range(net.shape[0]):
            for y in range(net.shape[1]):
                w = net[x, y, :].reshape(m, 1)
                # get the 2-D distance (again, not the actual Euclidean distance)
                w_dist = np.sum((np.array([x, y]) - bmu_idx) ** 2)
                # if the distance is within the current neighbourhood radius
                if w_dist <= r**2:
                    # calculate the degree of influence (based on the 2-D distance)
                    influence = calculate_influence(w_dist, r)
                    # now update the neuron's weight using the formula:
                    # new w = old w + (learning rate * influence * delta)
                    # where delta = input vector (t) - old w
                    new_w = w + (l * influence * (t - w))
                    # commit the new weight
                    net[x, y, :] = new_w.reshape(1, 3)



    fig = plt.figure()
    # setup axes
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_xlim((0, net.shape[0]+1))
    ax.set_ylim((0, net.shape[1]+1))
    ax.set_title('Self-Organising Map after %d iterations' % n_iterations)

    # plot the rectangles
    for x in range(1, net.shape[0] + 1):
        for y in range(1, net.shape[1] + 1):
            ax.add_patch(patches.Rectangle((x-0.5, y-0.5), 1, 1,
                         facecolor=net[x-1,y-1,:],
                         edgecolor='none'))

    # plt.set_size_inches(8, 8)
    plt.savefig(out_path, transparent=True, dpi=180)

    crop_photo(out_path)






from mage_ai.data_cleaner.transformer_actions.base import BaseAction
from mage_ai.data_cleaner.transformer_actions.constants import ActionType, Axis
from mage_ai.data_cleaner.transformer_actions.utils import build_transformer_action
from pandas import DataFrame

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from PIL import Image, ImageFilter

@transformer
def execute_transformer_action(filenames, filename_collage, *args, **kwargs) -> DataFrame:
    """
    Execute Transformer Action: ActionType.FILTER
    Docs: https://docs.mage.ai/guides/transformer-blocks#filter
    """

    rgb_colours, hex_colors, colors = get_colours(filename_collage, 8, True, filenames['pal'])
    rgb_colours = rgb_colours[0:7]

    bar = plot_colors2(rgb_colours)
    img = Image.fromarray(bar, 'RGB')
    img.save(filenames['col'])

    import numpy as np
    np_colors = np.array(rgb_colours)
    raw_data_test = np_colors.T

    get_som(raw_data_test, 1000, filenames['som'], 16)

    srciImage = Image.open(filenames['som'])
    gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
    gaussImage.save(filenames['spt'])
    gaussImage.save(filenames['new'])


    # get_som(collage_image, 1000, filenames['spt'], 16)
    # blurred_image = collage_image.filter(ImageFilter.BoxBlur(radius=2))
    # blurred_image.save(filenames['spt'])            
    # blurred_image.save(filenames['new'])
    # print(f'saved {filenames['spt']}')
    # img = Image.open(filenames['spt'])
    # img.save(filenames['new'])
    return filenames['spt']


    print(df, ff)
    return df, ff


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
