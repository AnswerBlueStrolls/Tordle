from utils.characters import replace_all_possible_name, the_same_name, replace_facial_features, load_characters_from_yaml_file
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
    res = load_characters_from_yaml_file("tests/test.yml")
    assert len(res) == 2
    assert len(res['斑'].alias) == 1
    testme = FaceOff("")
    testme.set_language("Chinese")
    testme.set_meta_characters(res)
    with open('tests/test.txt', 'r') as file:
        file_contents = file.read()
    testme.set_original_face_part(file_contents)
    after = testme.do_face_off()
    HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
    ner = HanLP['ner/msra']
    ner.dict_whitelist = {'三毛缟斑': 'PERSON', '樱河琥珀': 'PERSON', '三毛缟': 'PERSON', '斑': 'PERSON', '樱河': 'PERSON', '琥珀': 'PERSON'}
    #doc = HanLP(["斑说不⽤这么⿇烦，⼀起在床上睡就好了。我笑着说不⾏不⾏，我怕我会忍不住对琥珀做出不好的事。", "琥珀像被⽕烫到⼀样猛地抽回⾃⼰的⼿，放在⾝后，警戒地看着我。"], tasks='ner/msra').to_dict()
    doc = HanLP(file_contents.splitlines(), tasks='ner/msra').to_dict()
    print(doc['ner/msra'])
    assert len(after) != 0

