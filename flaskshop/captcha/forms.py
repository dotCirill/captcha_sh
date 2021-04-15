from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField

from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import random

letters = {}


class CaptchaForm(FlaskForm):
    answer = StringField("Answer")
    passwd: str
    imgs: List[Tuple[str, str]] # image, letters

    def __init__(self, *args, **kwargs):
        super(CaptchaForm, self).__init__(*args, **kwargs)
    
    def generate(self):
        self.passwd = current_user.email
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

        index = 0
        self.imgs = []
        random_coordinate = lambda: random.randint(0, piece_len - 1)
        letter_i = 0

        for i in range(IMG_COUNT):
            img = Image.new('RGBA', (piece_len, piece_len), '#223344')
            if letters_in_pieces[i] == 0:
                continue

            offset = int(piece_len/(letters_in_pieces[i] + 1)) + 10
            draw = ImageDraw.Draw(img)
            headline = ImageFont.truetype('/app/flaskshop/captcha/Roboto-Bold.ttf', size = offset)
            draw.text((offset/2, 40 - offset/2), self.passwd[index:index + letters_in_pieces[i]], font = headline)
            index += letters_in_pieces[i]
            for angle in (0, 45, 90, 180):
                for _ in range(random.randint(5, 7)):
                    draw.arc([random_coordinate(), random_coordinate(), random_coordinate(), random_coordinate()], 0, angle, fill='white', width=4)
            
            img = img.filter(ImageFilter.SMOOTH).filter(ImageFilter.BoxBlur(1.5))
            buffered = BytesIO()
            img.save(buffered, format='PNG')
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            self.imgs.append((img_str, self.passwd[letter_i:letter_i + letters_in_pieces[i]]))
            letter_i += letters_in_pieces[i]
        
        random.shuffle(self.imgs)
        letters[current_user.id] = ''
        for img in self.imgs:
            letters[current_user.id] += img[1] + '\n'

    def validate(self):
        answer_str = ''
        parts = letters[current_user.id].split('\n')
        for img_i in self.answer.data.split():
            if not img_i.isdigit():
                self.answer.errors = ["err1"]
                return False
            
            img_i = int(img_i)
            if not (img_i >= 0 and img_i < len(parts)):
                self.answer.errors = ["err2"]
                return False

            answer_str += parts[img_i]

        if answer_str != current_user.email:
            self.answer.errors = ["err3", answer_str]
            return False
        
        return True

