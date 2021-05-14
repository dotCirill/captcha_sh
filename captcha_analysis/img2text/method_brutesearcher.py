#!/usr/bin/env python3

from captcha_generate import GEN_DIR
import os
from PIL import Image
from dataclasses import dataclass
from tqdm import tqdm

MAX_DIST = 10**6

@dataclass
class Variant:
    file: str
    distance: int

def _distance(a, b, distance_to_stop=MAX_DIST):
    dist = 0
    for y in range(a.height):
        for x in range(a.width):
            ap = a.getpixel((x,y))
            bp = b.getpixel((x,y))
            for k in range(3):
                dist += abs(ap[k] - bp[k])
                if dist > distance_to_stop:
                    return MAX_DIST

    return dist

def translate(img_path: str, verbose=True):
    best = Variant(file="/dev/null", distance=MAX_DIST)
    input_img = Image.open(img_path)

    t = list(os.listdir("generated_captcha_images"))
    if verbose:
        t = tqdm(t)

    for filename in t:
        if not filename.endswith(".png"):
            continue

        img = Image.open(os.path.join(GEN_DIR, filename))

        d = _distance(img, input_img, distance_to_stop=best.distance)
        if d < best.distance:
            best.distance = d
            best.file = filename

        if verbose:
            t.set_description(f'{best.file} ({best.distance})')

    return os.path.basename(os.path.realpath(best.file))[:-len(".png")]
