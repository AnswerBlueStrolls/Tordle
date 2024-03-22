import yaml, math, os, random, re, datetime, json, textwrap
from faker import Faker
import utils.characters as characters, utils.db_connection as database
from PIL import Image, ImageDraw, ImageFont
class FaceOff:
    id = 0
    original_body = ""
    original_face_part = ""
    changed_face = ""
    changed_characters = {}
    config = {}
    exceptions = []
    meta_characters = {}
    special_names = []
    debug_mode = False
    base_path = ""

    def __init__(self, config_file):
        self.base_path = os.path.dirname(config_file)
        self.config = yaml.safe_load(open(config_file))
        self.config["db_name"] = os.path.join(self.base_path, self.config["db_name"])
        if self.config["debug"] == True:
            self.debug_mode = True
        db = database.AODatabase()
        db.init_from_config(self.config)
        self.id, self.original_body = db.get_one_fic_randomly()
        self.meta_characters = characters.load_characters_from_yaml_file(os.path.join(self.base_path, "characters.yml"))
        self.exceptions = characters.load_name_list_from_yaml_file(os.path.join(self.base_path, "exception_names.yml"))
        self.special_names = characters.load_name_list_from_yaml_file(os.path.join(self.base_path, "special_names.yml"))

    def choose_face_part(self):
        half = math.floor(len(self.original_body)/2)
        total = self.config["limit"]
        if half < total:
            total = half
        self.original_face_part = choose_piece(self.original_body, total)
    
    def mapping_meta_character(self, in_name):
        for first in self.meta_characters.keys():
            character = self.meta_characters[first]
            if character.is_the_same_person(in_name):
                return first
        return ""

    def find_characters(self):
        lang = self.config.get("language")
        if lang is None:
            lang = "English"
        #try nlp first
        nlp_characters = characters.find_characters_nlp(self.original_face_part, lang)
        for nlp_name in nlp_characters:
            if nlp_name in self.exceptions:
                continue
            if nlp_name is None or nlp_name == "":
                continue
            if nlp_name in self.special_names:
                self.changed_characters[nlp_name] = "HIDDEN_INFO"
                continue
            character_name = self.mapping_meta_character(nlp_name)
            if character_name != "": # found a match character
                self.changed_characters[character_name] = ""
                continue
            if self.debug_mode:
                self.ask_for_help(nlp_name)
        # Find the characters that are in the original face but not found by nlp
        for first in self.meta_characters.keys():
            character = self.meta_characters[first]
            if character.exist_in_text(self.original_face_part):
                self.changed_characters[first] = ""

    def find_avatars(self):
        for character in self.changed_characters.keys():
            if self.changed_characters[character] != "":
                continue
            self.changed_characters[character] = self.generate_random_name()

    def ask_for_help(self, name):
        question = "Not found this name: {}. Is it a correct name? (y/n)".format(name)
        ans = input(question).strip().lower()
        if ans == 'y':
            self.changed_characters[name] = ""
            return
        elif ans == 'n':
            print("Ignore this name.")
            return

    def generate_random_name(self):
        faker = Faker()
        full_name = faker.name()
        ret_name = full_name.split()[0]
        if ret_name in self.exceptions:
            return self.generate_random_name()
        else:
            return ret_name
    def do_replace_face(self):
        substitute = self.original_face_part
        for first in self.changed_characters:
            if first in self.meta_characters:
                character = self.meta_characters[first]
                substitute = character.replace(substitute, self.changed_characters[first])
            else:
                new_name = self.changed_characters[first]
                substitute = characters.simple_text_replace(substitute, first, new_name)
        return substitute
    
    def write_out(self, puzzle, answer):
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d_%H%M%S")
        puzzle_file_name = "{}-{}_puzzle.txt".format(time_string, str(self.id))
        image_file_name = "{}-{}_image.png".format(time_string, str(self.id))
        answer_file_name = "{}-{}_answer.txt".format(time_string, str(self.id))
        puzzle_dir = os.path.join(self.base_path, "puzzles")
        answer_dir = os.path.join(self.base_path, "answers")
        if not os.path.exists(puzzle_dir):
            os.makedirs(puzzle_dir)
        if not os.path.exists(answer_dir):
            os.makedirs(answer_dir)
        with open(os.path.join(puzzle_dir, puzzle_file_name), 'w') as file:
            wrapped = textwrap.fill(puzzle, 45, replace_whitespace=False)
            file.write(puzzle)
            print("puzzle generated")
            font = os.path.join(self.base_path, "font.ttf")
            img = text_to_image(wrapped, font, 28, 600, 10)
            img.save(os.path.join(puzzle_dir, image_file_name))

        with open(os.path.join(answer_dir, answer_file_name), 'w') as file:
            id_text = "work id: {}\n".format(str(self.id))
            file.write(id_text)
            json.dump(answer, file)
            print("answer generated")

    def face_off(self):
        self.choose_face_part()
        self.find_characters()
        if len(self.changed_characters) == 0:
            return False
        self.find_avatars()
        result = self.do_replace_face()
        if self.debug_mode:
            res = highlight_keywords_all(result, self.changed_characters.values())
            res = highlight_keywords_all(res, self.changed_characters.keys())
            print(res)
        self.write_out(result, self.changed_characters)
        return True

    


def text_to_image(text, font_path, font_size, image_width, margin):
    # Load a font
    font = ImageFont.truetype(font_path, font_size)
    line_spacing = 1.5
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
        text_width, text_height = draw.textsize(line, font=font)
        #x = (image_width - text_width) // 2
        draw.text((margin, y), line, fill='black', font=font)
        y += int(text_height * line_spacing)

    return img


def combine_piece(strings, start, end):
    selected_strings = strings[start:end+1]
    cleaned_list = list(filter(lambda line: line.strip(), selected_strings))
    return '\n'.join(cleaned_list)

def choose_piece(body, total):
    strings = body.splitlines()
    not_filled = True
    start_index = 0
    end_index = 0
    while not_filled:
        random_start = random.randint(0, len(strings) - 1)
        sum = 0
        start_index = random_start
        for i in range(random_start, len(strings)):
            if sum == 0 and len(strings[i]) < 3:
                start_index += 1
                continue
            sum += len(strings[i])
            if sum > total:
                end_index = i
                not_filled = False
                break  
    return combine_piece(strings, start_index, end_index)

def print_highlight_keywords(text, keyword_list):
    highlighted_text = text
    for keyword in keyword_list:
        highlighted_text = re.sub(r'\b' + re.escape(keyword) + r'\b', f'\033[91m{keyword}\033[0m', highlighted_text, flags=re.IGNORECASE)
    print(highlighted_text)

def highlight_keywords_all(text, keyword_list):
    highlighted_text = text
    for keyword in keyword_list:
        highlighted_text = re.sub(keyword, f'\033[91m{keyword}\033[0m', highlighted_text, flags=re.IGNORECASE)
    return highlighted_text