import yaml, math, os, datetime, json, textwrap, logging
from faker import Faker
import utils.characters as characters, utils.db_connection as database, utils.translator as trans
from utils.characters import CharacterManager, NameProcessor
import utils.string_functions as str_func
import utils.image as img_func
from opencc import OpenCC
from PIL import Image
bad_alias = ["Miss", "Amber", "Mr", "Mary", "Angelica", "Jesus", "Mr.", "Mrs.", "Dr."]
hidden_str = "HIDDEN_INFO"
hidden_color = "HIDDEN_COLOR"
logger = logging.getLogger(__name__)
class FaceOff:
    id = 0
    original_body = ""
    original_face_part = ""
    original_face_end_index = -1
    changed_face = ""
    changed_characters = {}
    config = {}
    exceptions = []
    meta_characters = {}
    special_names = []
    remove_names = []
    debug_mode = False
    base_path = ""
    tags = []
    db = None
    history = False
    read_mode = False
    web_mode = False
    language = ""
    text_length = 5399

    def __init__(self, config, id = 0, text_length = 0):
        if not config:
            print('config is empty')
            return
            
        self.config = config
        self.debug_mode = config.debug_mode
        self.read_mode = config.read_mode
        self.web_mode = config.web_mode
        self.language = config.language
        self.history = config.history
        if text_length < 0:
            self.text_length = -1
        else:
            self.text_length = self.config.get("limit")
        print(f'Read mode is {self.read_mode}')
        self.db = database.AODatabase()
        self.db.init_from_config(config.config)  # 暂时保持兼容性
        
        if id > 0:
            self.id = id
            self.original_body = self.db.get_fic_by_id(id)
        else:
            print(f'History is {self.history}')
            self.id, self.original_body, self.tags = self.db.get_one_fic_randomly(self.history)
        print(f'finished init, id is {self.id}')
        self.load_configs()

    def load_configs(self):
        self.language = self.config.language
        logger.info(f'config language is {self.language}')
        
        # 加载角色配置
        self.set_meta_characters(characters.load_characters_from_yaml_file(self.config.get_character_file()))
        
        # 加载特殊名称配置
        self.special_names = characters.load_name_list_from_yaml_file(self.config.get_special_names_file())
        
        if self.language == "English":
            self.exceptions = characters.load_name_list_from_yaml_file(self.config.get_exception_names_file())
        elif self.language == "Chinese":
            self.remove_names = characters.load_name_list_from_yaml_file(self.config.get_remove_names_file())

    def choose_face_part(self):
        # 如果是全文模式，直接使用全文
        if self.text_length == -1:
            print("Using full text")
            self.set_original_face_part(self.original_body)
            return
            
        half = math.floor(len(self.original_body)/2)
        if self.text_length is None:
             print("No limit set, use full text")
             self.set_original_face_part(self.original_body)
             return
        if half < self.text_length:
            print("fic is too short, use the whole fic, length is", len(self.original_body))
            self.original_face_part = self.original_body
            return
        self.original_face_part, self.original_face_end_index = str_func.choose_piece(self.original_body, self.text_length, self.original_face_end_index)
    
    def mapping_meta_character(self, in_name):
        for first in self.meta_characters.keys():
            character = self.meta_characters[first]
            tag = character.get_name("tag")
            if character.is_the_same_person(in_name):
                return first, tag
        return "", ""
    def reset(self):
        self.changed_characters.clear()
        self.tags.clear()
        self.original_body = ""
        self.original_face_part = ""
        self.original_face_end_index = -1

    def find_characters(self):
        if self.language is None:
            self.language = "English"
        #try nlp first
        print("text length is", len(self.original_face_part), "language is", self.language)
        if self.language == "English":
            found_characters = NameProcessor.find_characters_nlp(self.original_face_part)
        #elif self.language == "Chinese":
            #white_list = CharacterManager.get_whitelist(self.meta_characters)
            #found_characters = CharacterManager.find_characters_hanlp(self.original_face_part, white_list)
        if found_characters is None:
            return
        logger.info("Found {} nlp characters".format(len(found_characters)))
        if self.debug_mode or self.web_mode:
            print(found_characters)
        for nlp_name in found_characters:
            if nlp_name in self.exceptions:
                continue
            if nlp_name is None or nlp_name == "":
                continue
            if nlp_name in self.special_names:
                self.changed_characters[nlp_name] = hidden_str
                continue
            character_name, tag = self.mapping_meta_character(nlp_name)
            if character_name != "": # found a match character
                if self.debug_mode:
                    print("found character:", character_name, "nlp_name is", nlp_name)
                if self.language == "Chinese" and tag not in self.tags:
                    if len(nlp_name) < 2:
                        print("nlp_name is too short and not in tag, skip it", nlp_name)
                        continue
                if character_name not in self.changed_characters:
                    self.changed_characters[character_name] = ""
                continue
            if self.web_mode:
                logging.error("id: %d, name: %s", self.id, nlp_name)
                continue
            elif self.debug_mode or self.read_mode:
                self.ask_for_help(nlp_name)
            else:
                print("Error occurred.")
                if self.debug_mode:
                    print("name:", nlp_name)
                
        if self.debug_mode:
            print("after mapping changed character is ", self.changed_characters)
        if self.language == "English":
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
        question = "Not found this name: {} Add it then input y to reload or input n to ignore (y/n)".format(name)
        ans = input(question).strip().lower()
        if ans == 'y':
            self.changed_characters[name] = ""
            self.load_configs()
            return
        elif ans == 'n':
            print("Ignore this name.")
            return

    def generate_random_name(self):
        faker = Faker()
        full_name = faker.name()
        ret_name = full_name.split(' ')[0]
        if ret_name in self.exceptions:
            return self.generate_random_name()
        if ret_name in bad_alias:
            return self.generate_random_name()
        return ret_name
    def do_replace_face(self, substitute):
        for first in self.changed_characters:
            if first in self.meta_characters:
                character = self.meta_characters[first]
                substitute = character.replace(substitute, self.changed_characters[first], self.config.get("language"))
            else:
                new_name = self.changed_characters[first]
                substitute = characters.simple_text_replace(substitute, first, new_name, self.config.get("language"))
            if first == "Natsume":
                substitute = str_func.lowercase_end_of_words(substitute)
        return substitute
    def do_other_replace(self, substitute):
        # replace unfound special_names
        for special_name in self.special_names:
            substitute = characters.simple_text_replace(substitute, special_name, hidden_str, self.config.get("language"))
        substitute = characters.replace_facial_features(substitute, hidden_color)
        for remove_name in self.remove_names:
            substitute = characters.simple_text_replace(substitute, remove_name, "", self.config.get("language"))
        return substitute

    def puzzle_to_imgfile(self, puzzle, font, file_path, lang="English"):
        paragraphs = puzzle.strip().split('\n')
        file_width = 750
        width = 60
        fontsize = 28
        indent = "  "
        if lang == "Chinese":
            width = 30
            file_width = 900
            indent = "    "
        formatted_text = "\n"
        if self.read_mode:
            file_width = file_width*3
            fontsize = fontsize+10
            width = 70

        for paragraph in paragraphs:
            paragraph = indent+paragraph
            formatted_text += textwrap.fill(paragraph, width)
            formatted_text += "\n"
        print(f"generate file, width {file_width}, font size {fontsize}, read_mode {self.read_mode}")
        img = img_func.text_to_image(formatted_text, font, fontsize, file_width, 20, self.read_mode)
        img.save(file_path)
        print("File saved:", file_path)

    def write_out(self, puzzle, answer):
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d_%H%M%S")
        puzzle_file_name = "{}-{}_puzzle.txt".format(time_string, str(self.id))
        
        answer_file_name = "{}-{}_answer.txt".format(time_string, str(self.id))
        puzzle_dir = os.path.join(self.base_path, "puzzles")
        answer_dir = os.path.join(self.base_path, "answers")
        if not os.path.exists(puzzle_dir):
            os.makedirs(puzzle_dir)
        if not os.path.exists(answer_dir):
            os.makedirs(answer_dir)
        # read mode don't need answer.txt
        if not self.read_mode:
            with open(os.path.join(answer_dir, answer_file_name), 'w') as file:
                id_text = "work id: {}\n".format(str(self.id))
                file.write(id_text)
                json.dump(answer, file)
                print("Answer generated.")
        with open(os.path.join(puzzle_dir, puzzle_file_name), 'w') as file:
            file.write(puzzle)
            print("Puzzle generated.")
            original_font = "font_en.ttf"
            trans_font = "font_cn.ttf"
            original_file = "en.png"
            trans_file = "cn.png"
            org_lang = "English"
            trans_lang = "Chinese"
            if self.language == "Chinese":
                original_font = "font_cn.ttf"
                trans_font = "font_en.ttf"
                original_file = "cn.png"
                trans_file = "en.png"
                org_lang = "Chinese"
                trans_lang = "English"
            image_file_name = "{}-{}_image_{}".format(time_string, str(self.id), original_file)
            orgfont = os.path.join(self.base_path, "..", "common", original_font)
            org_img_path = os.path.join(puzzle_dir, image_file_name)
            puzzle = "{}/{}\n".format(len(self.original_face_part), len(self.original_body)) + puzzle
            self.puzzle_to_imgfile(puzzle, orgfont, org_img_path, lang=org_lang)
            if org_lang == "English":
                print("Start translator, DO NOT use mouse or keyboard!!!")
                puzzle = puzzle.replace(hidden_str, f"[{hidden_str}]")
                puzzle = puzzle.replace(hidden_color, f"[{hidden_color}]")
                tranlated_puzzle = trans.translate_with_deepl(puzzle)
                print("Puzzle translated.")
                transfont = os.path.join(self.base_path, "..", "common", trans_font)
                trans_img_path = os.path.join(puzzle_dir, image_file_name.replace(original_file, trans_file))
                self.puzzle_to_imgfile(tranlated_puzzle, transfont, trans_img_path, lang=trans_lang)
            else:
                img = Image.open(org_img_path)
                img.show()

    def set_meta_characters(self, characters):
        self.meta_characters = characters
    def set_original_face_part(self, body):
        self.original_face_part = body
    def set_language(self, language):
        self.config["language"] = language

    def do_face_off(self):
        self.find_characters()
        if len(self.changed_characters) == 0:
            print(f'Cannot find any characters, tags are: {self.tags}')
            return ""
        self.find_avatars()
        if self.debug_mode:
            print("changed characters: ",self.changed_characters)
        result = self.do_replace_face(self.original_face_part)
        result = self.do_other_replace(result)
        return result

    def get_face_off_content(self):
        self.choose_face_part()
        if self.language == "Chinese":
            cc = OpenCC('t2s')
            self.original_face_part = cc.convert(self.original_face_part)
        if len(self.original_face_part) == 0:
            print("Has no content")
            return -1
        result = self.do_face_off()
        all_characters = list(self.meta_characters.keys())
        return result, self.changed_characters, all_characters

    def repeat_face_off(self):
        if self.id == "" or self.id == 0 or self.id == '0':
            print("no id found")
            return -1
        print("ID: ", str(self.id))
        while True:
            result, _, _ = self.get_face_off_content()
            if len(result) == 0:
                return -1
            if self.debug_mode:
                res = str_func.highlight_keywords_all(result, self.changed_characters.values())
                res = str_func.highlight_keywords_all(result, self.special_names)
                res = str_func.highlight_keywords_all(res, self.changed_characters.keys())
                print(res)
            self.write_out(result, self.changed_characters)
            if not self.read_mode:
                return 1
            else:
                question = "Choose action: (C)ontinue / (S)kip / (L)ink / (A)nswer / (I)gnore / (E)xit:"
                ans = input(question).strip().lower()
                if ans == 'c':
                    continue
                elif ans == 's':
                    self.db.save_result_to_history(self.id, 0)
                    print(f'answer is {self.changed_characters}, tag is {self.tags}')
                    print("Remove this one, go to another work...")
                    return -1
                elif ans == 'l':
                    print("Save this one, and go to another work...")
                    print(f'answer is {self.changed_characters}, tag is {self.tags}')
                    self.db.save_result_to_history(self.id, 1)
                    # TODO: open the link
                    return -1
                elif ans == 'a':
                    print(f'answer is {self.changed_characters}, tag is {self.tags}')
                    continue
                elif ans == 'i':
                    print("Ignore this fanfic, find another one")
                    print(f'answer is {self.changed_characters}, tag is {self.tags}')
                    return -1
                elif ans == 'e':
                    return 1
