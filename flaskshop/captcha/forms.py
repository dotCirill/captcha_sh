from datetime import timedelta
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import HiddenField

from typing import List, Dict, Tuple
from collections import namedtuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import random
from redis import Redis
from flaskshop.settings import Config
from datetime import timedelta

# We are using Redis for storing img->letters converting
REDIS_DB_NUMBER = 5
CAPTCHA_TTL = timedelta(minutes=10) # time to live is redis db

rdb = Redis.from_url(Config.REDIS_URL, db=REDIS_DB_NUMBER)

# We store image as base64 because it will be easily forgotten after sending it to user with html
Piece = namedtuple('Piece', ['img_base64', 'letters'])

class CaptchaForm(FlaskForm):
    answer = HiddenField("") # permutation of images, set of numbers like "3 2 5 ..."
    passwd: str # email or another personal data 
    pieces: List[Piece]

    def __init__(self, *args, **kwargs):
        super(CaptchaForm, self).__init__(*args, **kwargs)
    
    def generate(self):
        self.passwd = current_user.email
        IMG_COUNT = 8
        PIECE_SIZE_PX = 100
        BG_COLOR = '#223344'
        FONT_FILE = '/app/flaskshop/captcha/Roboto-Bold.ttf'
        
        # distribution of letters between pictures
        piece_letters: List[str] = [""] * 8

        min_letters_in_piece = len(self.passwd) // 8
        remains = len(self.passwd) % 8
        pieces_without_extra_letter = list(range(8))
        for _ in range(remains):
            x = random.randint(0, len(pieces_without_extra_letter) - 1)
            pieces_without_extra_letter.pop(x)

        piece_i = 0
        letter_i = 0
        for letter in self.passwd:
            piece_letters[piece_i] += letter
            letter_i += 1
            extra_letter = 1 if piece_i not in pieces_without_extra_letter else 0
            if letter_i >= min_letters_in_piece + extra_letter:
                letter_i = 0
                piece_i += 1

        self.pieces = []
        random_coordinate = lambda: random.randint(0, PIECE_SIZE_PX - 1)

        for i in range(IMG_COUNT):
            img = Image.new('RGBA', (PIECE_SIZE_PX, PIECE_SIZE_PX), BG_COLOR)
            if not piece_letters[i]:
                continue

            offset = int(PIECE_SIZE_PX/(len(piece_letters[i]) + 1)) + 10
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(FONT_FILE, size=offset)
            draw.text((offset/2, 40 - offset/2), piece_letters[i], font=font)
           
            # add some stuff and filters
            for angle in (0, 45, 90, 180):
                for _ in range(random.randint(5, 7)):
                    draw.arc([random_coordinate(), random_coordinate(), random_coordinate(), random_coordinate()], 0, angle, fill='white', width=random.randint(3, 6))
            
            img = img.filter(ImageFilter.SMOOTH).filter(ImageFilter.BoxBlur(1.5))
            buffered = BytesIO()
            img.save(buffered, format='PNG')
            img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            piece = Piece(img_b64, piece_letters[i])
            self.pieces.append(piece)
        
        random.shuffle(self.pieces)
        
        letters = ''
        for piece in self.pieces:
            letters += piece.letters + '\n'

        rdb.setex(current_user.id, CAPTCHA_TTL, value=letters)

    def validate(self):
        answer_str = ''
        parts_lines = rdb.get(current_user.id)
        if not parts_lines:
            self.answer.errors = ["err4"]
            return False
        
        parts = parts_lines.decode('utf-8').split('\n')
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

