# import the necessary packages
from PIL import Image, ImageFilter
from PIL import ImageEnhance
import PIL.ImageOps
import pytesseract
import os

ENHANCE = 5 # 5, 8
TESSERACT_PSM = 7 # 7, 11, 12, 10, 13
RADIUS = 10
PERCENT = 150
TMP_FILENAME = "tmpimage.png"

def translate(img_path: str, verbose=True):
    image = Image.open(img_path).convert('RGB')
    image = PIL.ImageOps.invert(image)
    image = ImageEnhance.Brightness(image)
    image = image.enhance(ENHANCE)
    image = image.filter(ImageFilter.UnsharpMask(radius=RADIUS, percent=PERCENT))

    image.save(TMP_FILENAME)

    text: str = pytesseract.image_to_string(image, config=f'--psm {TESSERACT_PSM}')
    os.remove(TMP_FILENAME)
    return text.lower().strip().replace('(a)', '@').replace(' ', '')
