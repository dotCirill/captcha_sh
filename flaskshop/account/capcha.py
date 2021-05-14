from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import random

class Captcha:
    def __init__(self, passwd: str):
        self.passwd = passwd
        self.generate()
    
    def generate(self):
        IMG_COUNT = 8
        piece_len = 100
        min_letters_in_piece = int(len(self.passwd)/8)
        letters_in_pieces = []
        for i in range(0, 8):
            letters_in_pieces.append(min_letters_in_piece)

        if min_letters_in_piece * 8 < len(self.passwd):
            remains =  len(self.passwd) - (min_letters_in_piece * 8)
            for j in range(0, remains):
                letters_in_pieces[j] += 1


        capcha_width = 8 * (piece_len + 1)
        index = 0
        imgs = []
        random_coordinate = lambda: random.randint(0, piece_len - 1)

        for i in range(IMG_COUNT):
            img = Image.new('RGBA', (piece_len, piece_len), '#223344')
            if letters_in_pieces[i] == 0:
                continue

            offset = int(piece_len/(letters_in_pieces[i] + 1)) + 10
            draw = ImageDraw.Draw(img)
            headline = ImageFont.truetype('/app/flaskshop/account/Roboto-Bold.ttf', size = offset)
            draw.text((offset/2, 40 - offset/2), self.passwd[index:index + letters_in_pieces[i]], font = headline)
            index += letters_in_pieces[i]
            for angle in (0, 45, 90, 180):
                for _ in range(random.randint(5, 7)):
                    draw.arc([random_coordinate(), random_coordinate(), random_coordinate(), random_coordinate()], 0, angle, fill='white', width=4)
            
            img = img.filter(ImageFilter.SMOOTH).filter(ImageFilter.BoxBlur(1.5))
            imgs.append(img)
        
        random.shuffle(imgs)
        self.imgs = []
        for img in imgs:
            buffered = BytesIO()
            img.save(buffered, format='PNG')

            self.imgs.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
