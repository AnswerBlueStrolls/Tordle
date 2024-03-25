from PIL import Image, ImageDraw, ImageFont
import math, os
from utils.characters import load_name_list_from_yaml_file
script_location = os.path.dirname(os.path.abspath(__file__))
sensitive_words = load_name_list_from_yaml_file(os.path.join(script_location, "..", "metadata/common", "sensitive_words.yml"))
def find_sensitive_words_index(text):
    indexes = []
    for keyword in sensitive_words:
        index = text.find(keyword)
        if index >= 0:
            for i in range(index, index+len(keyword)):
                indexes.append(i)
    return sorted(indexes)

def text_to_image(text, font_path, font_size, image_width, margin):
    # Load a font
    font = ImageFont.truetype(font_path, font_size)
    line_spacing = 1
    # Create a drawing context to measure text size
    draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))

    # Calculate the number of lines and height required for the text
    lines = text.count('\n') + 1
    line_height = font.getsize(text)[1] * line_spacing
    text_height = lines * line_height 

    # Calculate the size of the image with margins
    image_height = math.floor(text_height + 2 * margin)

    # Create a blank image with a white background and margins
    img = Image.new('RGB', (image_width, image_height), color='white')
    img.info['dpi'] = (600, 600)
    # Initialize the drawing context
    draw = ImageDraw.Draw(img)

    # Calculate the position to center text vertically within margins
    y = margin + (text_height - lines * line_height) // 2

    for line in text.split('\n'):
        _, text_height = draw.textsize(line, font=font)
        words_index = find_sensitive_words_index(line)
        if len(words_index) == 0:
            x = margin
            draw.text((x, y), line, fill='black', font=font)
        else:
            print("Found sensitive words!")
            start = 0
            x = margin
            for i in words_index:
                if start < i:
                    draw.text((x, y), line[start:i], fill='black', font=font)
                    x += font.getsize(line[start:i])[0]
                    start = i
                if start == i:
                    # keyword
                    draw.text((x, y), line[i], fill='black', font=font)
                    character_width = font.getsize(line[i])[0]
                    draw.rectangle([(x, y+text_height/3), (x + character_width, y + text_height*0.8)], fill='red')
                    x += character_width
                    start += 1
        y += int(text_height * line_spacing)

    return img



