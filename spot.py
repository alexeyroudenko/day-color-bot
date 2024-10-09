import numpy as np
from colors.colors import get_colours
from colors.colors import plot_colors2
from colors.som import get_som
from PIL import Image, ImageFilter, ImageFile
import click

import logging
import logging.handlers

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('bot')  

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
    

  
'''
    Magic
'''  
def make_collages(images_paths, filename_collage):
    import math
    side_count = math.ceil(math.sqrt(len(images_paths)))
    logging.info(f'side_count {side_count}')
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
  
  
'''
    Magic
'''  
def make_spot(collage_path, phrase, folder):
    import cyrtranslit
    file_base = cyrtranslit.to_latin(phrase, "ru")
    # filename_collage  = f"{folder}{file_base}_src.jpg"
    filename_palette  = folder + file_base + "_pal.png"
    filename_col      = folder + file_base + "_col.png"
    filename_som      = folder + file_base + "_som.png"
    filename_blr      = folder + file_base + "_blr.png"
    
    rgb_colours, hex_colors, colors = get_colours(collage_path, 10, True, filename_palette)
    rgb_colours = rgb_colours[0:7]
    
    bar = plot_colors2(rgb_colours)
    img = Image.fromarray(bar, 'RGB')
    img.save(filename_col)

    np_colors = np.array(rgb_colours)
    raw_data_test = np_colors.T

    get_som(raw_data_test, 1000, filename_som, 16)

    srciImage = Image.open(filename_som)
    gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
    gaussImage.save(filename_blr)
    return filename_blr    

def get_collage_path(query):
    cfg['app']['tags_folder'] + f"{query}_src.jpg"
    
'''
Main
'''
@click.command()
@click.option("--query", default="morning", help="Query")
def make_spot_app(query:str) -> None:
    collage_path = cfg['app']['tags_folder'] + f"{query}_src.jpg"
    make_collages_folder(cfg['app']['tags_folder'] + f"/{query}/", collage_path)
    spot_path = make_spot(collage_path, query, cfg['app']['spot_folder'])
                
if __name__ == '__main__':
    make_spot_app()
        