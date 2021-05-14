#!/usr/bin/env python3

from method_tesseract import translate
#from method_CNN import translate
from tqdm import tqdm
import os

#t = list(os.listdir("generated_captcha_images"))
GEN_DIR = "./generated_captcha_images"
t = list (os.listdir(GEN_DIR))
t = tqdm(t)

success = 0
fail = 0

for filename in t:
    if not filename.endswith(".png"):
        continue
    
    fname = os.path.join(GEN_DIR, filename)
    real = filename[:-4]
    translated = translate(fname)
    
    fail += abs(len(real) - len(translated))
    for i in range(min(len(real), len(translated))):
        if real[i] == translated[i]:
            success += 1
        else:
            fail += 1
    
    t.set_description(f'{100 * success / (success + fail):.3}%')

print(f'Final result: {100 * success / (success + fail):.3}%')
