from utils.characters import replace_all_possible_name, the_same_name, replace_facial_features
from utils.image import find_sensitive_words_index


def test_replace_all_possible_name():
    result = replace_all_possible_name("Eichi", "Allen", "E-Eichi-san please fuck Eichi.")
    assert result == "Allen please fuck Allen."

def test_find_sensitive_words_index():
    result = find_sensitive_words_index("他舔着沿着大腿留下的精液")
    assert result == [1, 2, 5, 6, 10, 11]

def test_the_same_name():
    result = the_same_name("Kohaku", "Kohaku-san")
    assert result == "Kohaku"

def testreplace_facial_features():
    body = "showing off his sharp teeth with his wide grin"
    result = replace_facial_features(body, "")
    assert result == "showing off his teeth with his wide grin"
    body = "The blue-haired man fixes himself"
    result = replace_facial_features(body, "abc")
    assert result == "The abc-haired man fixes himself"