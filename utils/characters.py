import yaml, re, spacy

character_keys = ['full','full_revert', 'first', 'last']
class Character:
    first = ""
    last = ""
    full = ""
    full_revert = ""
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
                return self.full_revert
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
            if re.search(r'\b' + re.escape(name) + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(name+"'s") + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(name.lower()) + r'\b', body):
                return True
        for alien in self.alias:
            if re.search(r'\b' + re.escape(alien) + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(alien)+"'s" + r'\b', body):
                return True
            if re.search(r'\b' + re.escape(alien.lower()) + r'\b', body):
                return True

    def replace(self, body, new_name):
        for key in character_keys:
            old_name = self.get_name(key)
            if len(old_name) == 0:
                continue
            pattern = r'\b' + re.escape(old_name) + r'\b'
            body = re.sub(pattern, new_name, body)
            pattern = r'\b' + re.escape(old_name+"'s") + r'\b'
            body = re.sub(pattern, new_name+"'s", body)
            pattern = r'\b' + re.escape(old_name.lower()) + r'\b'
            body = re.sub(pattern, new_name, body)
        for alien in self.alias:
            pattern = r'\b' + re.escape(alien) + r'\b'
            body = re.sub(pattern, new_name, body)
            pattern = r'\b' + re.escape(alien+"'s") + r'\b'
            body = re.sub(pattern, new_name+"'s", body)
            pattern = r'\b' + re.escape(alien.lower()) + r'\b'
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

def load_exception_names_from_yaml_file(file_path):
    exception_names = []
    with open(file_path, 'r') as stream:
        try:
            exception_names = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return exception_names




nlp_lang_dict = {"English": "en_core_web_sm", "Chinese": "zh_core_web_sm"}
def find_characters_nlp(text, language):
    if language not in nlp_lang_dict:
        return []
    nlp = spacy.load(nlp_lang_dict[language])
    doc = nlp(text)
    person_names = []
    current_person = ""
    for token in doc:
        if token.ent_type_ == "PERSON":
            current_person += token.text + " "
        elif current_person:
            person_names.append(current_person.strip()) 
            current_person = ""
    if current_person:
        person_names.append(current_person.strip())
    return list(set(person_names))

'''
find out if the two names are the same
'''
def the_same_name(name_meta, name_body):
    name1 = name_meta.lower()
    name2 = name_body.lower()
    if name1 == name2:
        return name1
    if re.search(r'\b' + re.escape("-") + r'\b', name_body): # the body name is like xxx-san
        return the_same_name(name_meta.split()[0], name_body.split()[0])
    return ""

