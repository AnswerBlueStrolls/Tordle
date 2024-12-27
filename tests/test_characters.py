import pytest
from typing import Dict
from utils.characters import (
    Character,
    EnglishTextProcessor,
    ChineseTextProcessor,
    CharacterManager,
    replace_facial_features,
    compare_names
)
from utils.image import find_sensitive_words_index
from aesthetic.face_off import FaceOff

@pytest.fixture
def english_processor():
    return EnglishTextProcessor()

@pytest.fixture
def chinese_processor():
    return ChineseTextProcessor()

@pytest.fixture
def sample_character():
    return Character(
        first="Eichi",
        last="Tenshouin",
        full="Eichi Tenshouin",
        alias=["Emperor"]
    )

class TestTextProcessors:
    def test_english_name_replacement(self, english_processor):
        """测试英文名字替换功能"""
        text = "E-Eichi-san please help Eichi. Eichi's book."
        result = english_processor.replace_name("Eichi", "Allen", text)
        assert "Allen please help Allen. Allen's book." == result

    def test_chinese_name_replacement(self, chinese_processor):
        """测试中文名字替换功能"""
        text = "英智君请帮帮英智"
        result = chinese_processor.replace_name("英智", "天祥院", text)
        assert "天祥院君请帮帮天祥院" == result

class TestCharacter:
    def test_character_initialization(self, sample_character):
        """测试角色初始化"""
        assert sample_character.first == "Eichi"
        assert sample_character.last == "Tenshouin"
        assert "Emperor" in sample_character.alias

    def test_is_same_person(self, sample_character):
        """测试人物对比功能"""
        assert sample_character.is_the_same_person("Eichi-san")
        assert sample_character.is_the_same_person("Emperor")
        assert not sample_character.is_the_same_person("Wataru")

    def test_exist_in_text(self, sample_character):
        """测试文本中人物存在检查"""
        text = "Eichi's book belongs to Emperor"
        assert sample_character.exist_in_text(text)
        
        text = "This text doesn't contain the character"
        assert not sample_character.exist_in_text(text)

class TestCharacterManager:
    def test_load_characters(self):
        """测试从YAML文件加载角色"""
        characters = CharacterManager.load_characters("tests/test.yml")
        assert isinstance(characters, dict)

    def test_load_name_list(self):
        """测试加载名字列表"""
        names = CharacterManager.load_name_list("tests/test.yml")
        assert isinstance(names, list)

def test_compare_names():
    """测试名字比较功能"""
    assert compare_names("Kohaku", "Kohaku-san")
    assert compare_names("EICHI", "eichi")
    assert not compare_names("Wataru", "Eichi")
    assert not compare_names("", "Eichi")

def test_replace_facial_features():
    """测试面部特征替换功能"""
    # 测试基本替换
    text = "showing off his sharp teeth with his wide grin"
    result = replace_facial_features(text, "")
    assert result == "showing off his teeth with his wide grin"

    # 测试发色替换
    text = "The blue-haired man fixes himself"
    result = replace_facial_features(text, "abc")
    assert result == "The abc-haired man fixes himself"

    # 测试多种颜色和特征
    text = "A person with red eyes and black hair"
    result = replace_facial_features(text, "hidden")
    assert "hidden eyes" in result
    assert "hidden hair" in result

def test_find_sensitive_words_index():
    """测试敏感词检测"""
    result = find_sensitive_words_index("他舔着沿着大腿留下的精液")
    assert result == [1, 2, 5, 6, 10, 11]

@pytest.mark.skip(reason="Temporarily skipping Chinese integration test")
def test_chinese_integration():
    """暂时跳过中文集成测试"""
    testme = FaceOff("metadata/ensemble_stars/config.yml")
    testme.set_language("Chinese")
    testme.load_configs()
    
    # 测试白名单生成
    characters = testme.meta_characters
    whitelist = {
        name: 'PERSON'
        for char in characters.values()
        for name in [char.first, char.last, char.full] + char.alias
        if name
    }
    assert len(whitelist) > 0

    # 测试文本处理
    with open('tests/test.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    
    testme.set_original_face_part(text)
    testme.tags = ['Mikejima Madara', 'Oukawa Kohaku']
    result = testme.do_face_off()
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0

if __name__ == '__main__':
    pytest.main(['-v'])

