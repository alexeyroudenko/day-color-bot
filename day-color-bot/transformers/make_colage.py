from __future__ import division
import numpy as np
from PIL import Image
from PIL import Image, ImageFilter, ImageFile
import math



  
def make_filenames():  
    fnames = {}
    import datetime
    file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    import pathlib
    out_folder = "./data/trends/"             
    fnames['txt'] = pathlib.PurePath(out_folder + file_base + ".txt").as_posix()
    fnames['src'] = pathlib.PurePath(out_folder + file_base + "_src.jpg").as_posix()
    fnames['pal'] = pathlib.PurePath(out_folder + file_base + "_pal.jpg").as_posix()
    fnames['col'] = pathlib.PurePath(out_folder + file_base + "_col.jpg").as_posix()
    fnames['som'] = pathlib.PurePath(out_folder + file_base + "_som.jpg").as_posix()
    fnames['spt'] = pathlib.PurePath(out_folder + file_base + ".jpg").as_posix()
    fnames['new'] = pathlib.PurePath(out_folder + "spot" + ".jpg").as_posix()
    return fnames


def make_collage(rimages):
    filenames = make_filenames()
    out_folder = "./"
    file_base = "word"
    images = rimages[0]   
    side_count = math.ceil(math.sqrt(len(images)))
    filename_collage = filenames['src']
    
    if not rimages:
        print('No images for making collage! Please select other directory with images!')
    else:
        print(f"make collage {filename_collage}")

    w = int(1024/side_count)
    h = int(1024/side_count)
    size = int(w/side_count)
    collage_image = Image.new('RGB', (w, h), (35, 35, 35))
    
    latest_image = None
    
    for i, img_path in enumerate(images):
        print(f"{i} {img_path}") 
        # img_path = f"{collect_folder}{tag}/Image_1.jpg"
        img = None        
        try:
            img = Image.open(img_path)

            s = 113
            img = img.resize(size=(s, s)).convert('RGB')
            latest_image = img
            img.save(img_path, "JPEG")
        except Exception:    
            img = latest_image

        if img != None:                         
            collage_image.paste(img, ((i % side_count) * size, int(i / side_count) * size))    
            
    print(f"fmasave collage {filename_collage}")
    collage_image.save(filename_collage)
    return filename_collage


@transformer
def execute_transformer_action(files, *args, **kwargs):    
    return make_collage(files)



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
