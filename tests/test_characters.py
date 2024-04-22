from utils.characters import replace_all_possible_name, the_same_name, replace_facial_features, load_characters_from_yaml_file, get_whitelist
from utils.image import find_sensitive_words_index
from aesthetic.face_off import FaceOff
import hanlp


def test_replace_all_possible_name():
    result = replace_all_possible_name("Eichi", "Allen", "E-Eichi-san please fuck Eichi.")
    assert result == "Allen please fuck Allen."

def test_find_sensitive_words_index():
    result = find_sensitive_words_index("他舔着沿着大腿留下的精液")
    assert result == [1, 2, 5, 6, 10, 11]

def test_the_same_name():
    result = the_same_name("Kohaku", "Kohaku-san")
    assert result == "Kohaku"

def test_replace_facial_features():
    body = "showing off his sharp teeth with his wide grin"
    result = replace_facial_features(body, "")
    assert result == "showing off his teeth with his wide grin"
    body = "The blue-haired man fixes himself"
    result = replace_facial_features(body, "abc")
    assert result == "The abc-haired man fixes himself"

def test_chinese():
    testme = FaceOff("metadata/ensemble_stars/config.yml")
    testme.set_language("Chinese")
    testme.load_configs()
    whitelist = get_whitelist(testme.meta_characters)
    assert(len(whitelist) > 0)
    with open('tests/test.txt', 'r') as file:
        file_contents = file.read()
    testme.set_original_face_part(file_contents)
    after = testme.do_face_off()
    print(after)
    assert len(after) != 0

