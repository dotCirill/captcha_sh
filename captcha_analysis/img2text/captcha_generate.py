#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
from tqdm import tqdm
from itertools import product
from os import path, makedirs
from math import inf, isinf

GENERATE_CLEAN = False
ALPHABET = string.ascii_lowercase + '@' + '.' + string.digits
PIECE_SIZE_PX = 100
BG_COLOR = '#223344'
FONT_FILE = 'Roboto-Bold.ttf'
#FONT_FILE = 'OpenSans-SemiBold.ttf'
LETTERS_IN_IMAGE_MAX = 3
COUNTS = (inf, inf, inf) if GENERATE_CLEAN else (inf, inf, inf) # for NN training
#COUNTS = (inf, inf, inf)
GEN_DIR = 'generated_captcha_images_clean' if GENERATE_CLEAN else 'generated_captcha_images'
random_coordinate = lambda: random.randint(0, PIECE_SIZE_PX - 1)

if __name__ == "__main__":
    makedirs(GEN_DIR, exist_ok=True)
    for letters in tqdm(range(1, LETTERS_IN_IMAGE_MAX + 1), colour="BLUE", leave=False):
        offset = int(PIECE_SIZE_PX/(letters + 1)) + 10
        font = ImageFont.truetype(FONT_FILE, size=offset)

        generate_list = list(product(ALPHABET, repeat=letters))
        if len(ALPHABET)**(letters) > COUNTS[letters - 1]:
            generate_list = random.sample(generate_list, k=COUNTS[letters - 1])

        for p in tqdm(generate_list, colour="RED", leave=False):
            text = ''.join(p)
            fname = f'{text}.png'
            img = Image.new('RGBA', (PIECE_SIZE_PX, PIECE_SIZE_PX), BG_COLOR)
            draw = ImageDraw.Draw(img)
            draw.text((offset/2, 40 - offset/2), text, font=font)
            if not GENERATE_CLEAN:
                for angle in (0, 45, 90, 180):
                    for _ in range(random.randint(5, 7)):
                        draw.arc([random_coordinate(), random_coordinate(), random_coordinate(), random_coordinate()], 0, angle, fill='white', width=random.randint(3, 6))

            img = img.filter(ImageFilter.SMOOTH).filter(ImageFilter.BoxBlur(1.5))
            img.save(path.join(GEN_DIR, fname), format='PNG')

