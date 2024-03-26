from utils.characters import replace_all_possible_name, the_same_name
from utils.image import find_sensitive_words_index
import os

def test_replace_all_possible_name():
    result = replace_all_possible_name("Eichi", "Allen", "E-Eichi-san please fuck Eichi.")
    assert result == "Allen please fuck Allen."

def test_find_sensitive_words_index():
    result = find_sensitive_words_index("他舔着沿着大腿留下的精液")
    assert result == [1, 2, 5, 6, 10, 11]

def test_the_same_name():
    result = the_same_name("Kohaku", "Kohaku-san")
    assert result == "Kohaku"

