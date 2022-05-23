from io import BytesIO

import requests as requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "files/ticket-base.png"
FONT_PATH = "files/Roboto-Regular.ttf"
FONT_SIZE = 20

BLACK = (0, 0, 0, 255)
NAME_OFFSET = (280, 145)
EMAIL_OFFSET = (280, 190)

AVATAR_SIZE = 100
AVATAR_OFFSET = (100, 100)

def generate_ticket(name, email):
    with Image.open(TEMPLATE_PATH).convert("RGBA") as base:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        draw = ImageDraw.Draw(base)
        draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
        draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)

        response = requests.get(url=f'http://api.adorable.io/avatars/{AVATAR_SIZE}/{email}')
        avatar_file_like = BytesIO(response.content)
        avatar = Image.open(avatar_file_like)

        base.paste(avatar, AVATAR_OFFSET)

        temp_file = BytesIO()
        base.save(temp_file, 'png')
        temp_file.seek(0)

        return temp_file

        # with open('files/ticket-example.png', 'wb') as f:
        #     base.show(f, 'png')