from PIL import Image, ImageFilter

import glob
for i, infile in enumerate(glob.glob('data/**/[0-9].jpg', recursive=True)):
    s = 128
    quality_val = 80
    if i < 5000:
        try:
            im = Image.open(infile)
            # im.thumbnail((s, s))
            print(infile, im.size[0])
            if im.size[0] > 128:
                im = im.resize(size=(s, s)).convert('RGB')            
                im.save(infile, "JPEG")
        except:
            ...
    