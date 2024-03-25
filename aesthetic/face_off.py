import yaml, math, os, datetime, json, textwrap, logging
from faker import Faker
import utils.characters as characters, utils.db_connection as database, utils.translator as trans
import utils.string_functions as str_func
import utils.image as img_func
bad_alias = ["Miss", "Amber", "Mr"]
hidden_str = "(HIDDEN_INFO)"
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
        self.original_face_part = str_func.choose_piece(self.original_body, total)
    
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
                self.changed_characters[nlp_name] = hidden_str
                continue
            character_name = self.mapping_meta_character(nlp_name)
            if character_name != "": # found a match character
                self.changed_characters[character_name] = ""
                continue
            if self.debug_mode:
                self.ask_for_help(nlp_name)
            else:
                print("Error occurred.")
                logging.error("id: %d, name: %s", self.id, nlp_name)
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
        if ret_name in bad_alias:
            return self.generate_random_name()
        return ret_name
    def do_replace_face(self, substitute):
        for first in self.changed_characters:
            if first in self.meta_characters:
                character = self.meta_characters[first]
                substitute = character.replace(substitute, self.changed_characters[first])
            else:
                new_name = self.changed_characters[first]
                substitute = characters.simple_text_replace(substitute, first, new_name)
            if first == "Natsume":
                substitute = str_func.lowercase_end_of_words(substitute)
        return substitute
    def do_other_replace(self, substitute):
        # replace unfound special_names
        for special_name in self.special_names:
            substitute = characters.simple_text_replace(substitute, special_name, hidden_str)
        return substitute

    def puzzle_to_imgfile(self, puzzle, font, file_path, lang="English"):
        paragraphs = puzzle.strip().split('\n')
        file_width = 750
        width = 60
        indent = "  "
        if lang == "Chinese":
            width = 30
            file_width = 900
            indent = "    "
        formatted_text = "\n"
        for paragraph in paragraphs:
            paragraph = indent+paragraph
            formatted_text += textwrap.fill(paragraph, width)
            formatted_text += "\n"
        img = img_func.text_to_image(formatted_text, font, 28, file_width, 20)
        img.save(file_path)
        print("File saved:", file_path)

    def write_out(self, puzzle, answer):
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d_%H%M%S")
        puzzle_file_name = "{}-{}_puzzle.txt".format(time_string, str(self.id))
        image_file_name = "{}-{}_image_en.png".format(time_string, str(self.id))
        answer_file_name = "{}-{}_answer.txt".format(time_string, str(self.id))
        puzzle_dir = os.path.join(self.base_path, "puzzles")
        answer_dir = os.path.join(self.base_path, "answers")
        if not os.path.exists(puzzle_dir):
            os.makedirs(puzzle_dir)
        if not os.path.exists(answer_dir):
            os.makedirs(answer_dir)
        with open(os.path.join(answer_dir, answer_file_name), 'w') as file:
            id_text = "work id: {}\n".format(str(self.id))
            file.write(id_text)
            json.dump(answer, file)
            print("Answer generated.")
        with open(os.path.join(puzzle_dir, puzzle_file_name), 'w') as file:
            file.write(puzzle)
            print("Puzzle generated.")
            print("Start translator, DO NOT use mouse or keyboard!!!")
            tranlated_puzzle = trans.translate_with_deepl(puzzle)
            print("Puzzle translated.")
            enfont = os.path.join(self.base_path, "font_en.ttf")
            en_img_path = os.path.join(puzzle_dir, image_file_name)
            self.puzzle_to_imgfile(puzzle, enfont, en_img_path)
            cnfont = os.path.join(self.base_path, "font_cn.ttf")
            cn_img_path = os.path.join(puzzle_dir, image_file_name.replace("en.png", "cn.png"))
            self.puzzle_to_imgfile(tranlated_puzzle, cnfont, cn_img_path, lang="Chinese")


    def face_off(self):
        self.choose_face_part()
        self.find_characters()
        if len(self.changed_characters) == 0:
            return False
        self.find_avatars()
        print("ID: ", str(self.id))
        result = self.do_replace_face(self.original_face_part)
        result = self.do_other_replace(result)
        if self.debug_mode:
            res = str_func.highlight_keywords_all(result, self.changed_characters.values())
            res = str_func.highlight_keywords_all(result, self.special_names)
            res = str_func.highlight_keywords_all(res, self.changed_characters.keys())
            print(res)
        self.write_out(result, self.changed_characters)
        return True
