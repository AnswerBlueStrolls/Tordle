import yaml, math, os, random, re
from faker import Faker
import utils.characters as characters, utils.db_connection as database
class FaceOff:
    id = 0
    original_body = ""
    original_face_part = ""
    changed_face = ""
    changed_characters = {}
    config = {}
    exceptions = []
    meta_characters = []

    def __init__(self, config_file):
        base_path = os.path.dirname(config_file)
        self.config = yaml.safe_load(open(config_file))
        self.config["db_name"] = os.path.join(base_path, self.config["db_name"])
        db = database.AODatabase()
        db.init_from_config(self.config)
        self.id, self.original_body = db.get_one_fic_randomly()
        self.meta_characters = characters.load_characters_from_yaml_file(os.path.join(base_path, "characters.yml"))
        self.exceptions = characters.load_exception_names_from_yaml_file(os.path.join(base_path, "exception_names.yml"))
    def choose_face_part(self):
        half = math.floor(len(self.original_body)/2)
        total = self.config["limit"]
        if half < total:
            total = half
        self.original_face_part = choose_piece(self.original_body, total)
    
    def mapping_meta_character(self, in_name):
        for character in self.meta_characters:
            if character.is_the_same_person(in_name):
                return character.first
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
            character_name = self.mapping_meta_character(nlp_name)
            if character_name != "": # found a match character
                self.changed_characters[character_name] = ""
                continue
            self.ask_for_help(nlp_name)
           

        # Find the characters that are in the original face but not found by nlp
        for character in self.meta_characters:
            if character.exist_in_text(self.original_face_part):
                self.changed_characters[character.first] = ""
    def find_avatars(self):
        for character in self.changed_characters.keys():
            print(character)
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
        print("avatar is ", ret_name)
        if ret_name in self.exceptions:
            return self.generate_random_name()
        else:
            return ret_name

    def face_off(self):
        self.choose_face_part()
        self.find_characters()
        print_highlight_keywords(self.original_face_part, self.changed_characters.keys())
        self.find_avatars()
        print(self.changed_characters)

    

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