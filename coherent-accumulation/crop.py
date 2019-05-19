from glob import glob
from PIL import Image

imgs = glob('cancellation_pics/*.png')


for img in imgs:
    print(img, end='\t')
    im = Image.open(img)
    width, height = im.size
    print('crop', end='\t')
    im_cropped = im.crop((0, 0, 992, height))
    print('save', end='\t')
    im_cropped.save(img)
    print('done', end='\n')
