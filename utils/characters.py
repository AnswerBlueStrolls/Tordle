import yaml, re, spacy

character_keys = ['full','full_revert', 'first', 'last']
class Character:
    first = ""
    last = ""
    full = ""
    full_revert = ""
    tag = ""
    alias = []
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

    def get_name(self, key):
        match key:
            case 'first':
                return self.first
            case 'last':
                return self.last
            case 'full':   
                return self.full
            case 'full_revert':
                if self.full_revert != None and len(self.full_revert) > 0:
                    return self.full_revert
                else:
                    return ""
        return ""
    def print(self):
        template = "Idol: {} {}. Nick names: {}".format(self.first, self.last, self.alias)
        print(template)

    def is_the_same_person(self, in_name):
        for key in character_keys:
            res = the_same_name(self.get_name(key), in_name)
            if len(res) > 0:
                return True
        for alien in self.alias:
            res = the_same_name(alien, in_name)
            if len(res) > 0:
                return True
        return False
    def exist_in_text(self, body):
        for key in character_keys:
            name = self.get_name(key)
            if re.search(r'\b' + re.escape(name+"'s") + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(name) + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(name.lower()) + r'\b', body):
                return True
        for alien in self.alias:
            if re.search(r'\b' + re.escape(alien)+"'s" + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(alien) + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(alien.lower()) + r'\b', body):
                return True
    

    def replace(self, body, new_name):
        for key in character_keys:
            old_name = self.get_name(key)
            if len(old_name) == 0:
                continue
            body = replace_all_possible_name(old_name, new_name, body)
        for alien in self.alias:
            old_name = alien
            if "-" in alien:
                old_name = re.sub(r'\s+', '', alien)
            body = replace_all_possible_name(old_name, new_name, body)
        return body

def replace_all_possible_name(replaced_name, new_name, body):
    base = [replaced_name, replaced_name.lower(), replaced_name.upper()]
    for old_name in base:
        pattern = r'\b(\w+-)?' + re.escape(old_name) + r'(-\w+[?!.~]*)?\b'
        body = re.sub(pattern, new_name, body)
        pattern = r'\b' + re.escape(old_name+"'s") + r'\b'
        body = re.sub(pattern, new_name+"'s", body)
        pattern = r'\b' + re.escape(old_name+"s") + r'\b'
        body = re.sub(pattern, new_name+"'s", body)
        pattern = r'\b\.*' + re.escape(old_name) + r'\.*\b'
        body = re.sub(pattern, new_name+"'s", body)
        pattern = r'\b\.*' + re.escape(old_name+"~") + r'\.*\b'
        body = re.sub(pattern, new_name+"~", body)
        pattern = r'\b' + re.escape(old_name) + r'\b'
        body = re.sub(pattern, new_name, body)
    return body

def load_characters_from_yaml_file(file_path):
    characters = []
    characters_objs = {}
    with open(file_path, 'r') as stream:
        try:
            characters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    for c in characters:
        new_character = Character(c)
        characters_objs[new_character.first] = new_character
    return characters_objs

def load_name_list_from_yaml_file(file_path):
    name_list = []
    with open(file_path, 'r') as stream:
        try:
            name_list = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return name_list

def simple_text_replace(body, replaced_name, new_name):
    base = [replaced_name, replaced_name+"'s", replaced_name.lower(), replaced_name.upper()]
    for old_name in base:
        pattern = r'\b' + re.escape(old_name) + r'\b'
        body = re.sub(pattern, new_name, body)
    return body

def replace_eyes_and_hair(body, color, after):
    body = body.replace(color + " eyes", after+" eyes")
    body = body.replace(color + " hair", after+" hair")
    body = body.replace(color + "-haired", after+"-haired")
    body = body.replace(color + "head", after+"head")
    body = body.replace(color + " strand", after+"head")
    body = body.replace(color + " strands", after+"head")
    return body
def replace_facial_features(body, color_hidden_str):
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "purple", "pink", "brown", "black", "white", "gray", "silver", "gold", "raven", "crimson", "beaujolais", "cerulean", "sakura", "mint", "ginger"]
    for color in colors:
        body = replace_eyes_and_hair(body, color, color_hidden_str)
        body = replace_eyes_and_hair(body, color.capitalize(), color_hidden_str)
    body = body.replace("sharp teeth", "teeth")
    body = body.replace("Sharp teeth", "Teeth")
    single_words = ["blonde", "blond", "blondish", "blondness"]
    for word in single_words:
        pattern = r'\b'+word+r'\b'
        body = re.sub(pattern, color_hidden_str, body)
        pattern = r'\b'+word.capitalize()+r'\b'
        body = re.sub(pattern, color_hidden_str, body)
    return body

def find_characters_nlp(text, language):
    person_names = []
    current_person = ""
    if language == "English":
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for token in doc:
            if token.ent_type_ == "PERSON":
                current_person += token.text + " "
            elif current_person:
                person_names.append(current_person.strip()) 
                current_person = ""
        if current_person:
            person_names.append(current_person.strip())
        return list(set(person_names))
    if language == "Chinese":
        return []

'''
find out if the two names are the same
'''
def the_same_name(name_meta, name_body):
    if len(name_meta) == 0 or len(name_body) == 0:
        return ""
    name1 = name_meta.lower()
    name2 = name_body.lower()
    if name1 == name2:
        return name_meta
    if "-" in name_body: # the body name is like xxx-san
        return the_same_name(name_meta.split('-')[0].strip(), name_body.split('-')[0].strip())
    return ""

