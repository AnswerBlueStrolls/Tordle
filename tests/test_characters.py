from Tordle.utils.characters import replace_all_possible_name
from Tordle.utils.image import find_sensitive_words_index, text_to_image
import os

def test_replace_all_possible_name():
    result = replace_all_possible_name("Eichi", "Allen", "E-Eichi-san please fuck Eichi.")
    assert result == "Allen please fuck Allen."

def test_find_sensitive_words_index():
    result = find_sensitive_words_index("他舔着沿着大腿留下的精液")
    assert result == [1, 2, 5, 6, 10, 11]

def test_text_to_image():
    testdir = os.path.dirname(os.path.abspath(__file__))
    font = os.path.join(testdir, "..", "metadata/common/font_cn.ttf")
    text = "他舔着沿着大腿留下的精液"
    img = text_to_image(text, font, 28, 600, 20)
    img.show()
