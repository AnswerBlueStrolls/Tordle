from typing import Dict, List, Optional
import yaml
import re
import spacy
import hanlp
import os
import logging
from dataclasses import dataclass, field

# 配置日志记录器
logger = logging.getLogger(__name__)

@dataclass
class Character:
    """表示一个角色的类，使用dataclass简化类的定义"""
    first: str = ""
    last: str = ""
    full: str = ""
    full_revert: str = ""
    tag: str = ""
    alias: List[str] = field(default_factory=list)

    NAME_KEYS = ['full', 'full_revert', 'first', 'last']

    def get_name(self, key: str) -> str:
        """获取指定类型的名字"""
        if key == 'full_revert':
            return self.full_revert if self.full_revert else ""
        return getattr(self, key, "")

    def __str__(self) -> str:
        """返回角色的字符串表示"""
        return f"Character: {self.first} {self.last}. Nicknames: {self.alias}"

    def is_the_same_person(self, input_name: str) -> bool:
        """检查输入的名字是否指向同一个角色"""
        # 检查所有可能的名字形式
        for key in self.NAME_KEYS:
            if compare_names(self.get_name(key), input_name):
                return True
        # 检查别名
        return any(compare_names(alias, input_name) for alias in self.alias)

    def exist_in_text(self, text: str) -> bool:
        """检查角色是否在文本中出现"""
        def check_name_existence(name: str) -> bool:
            if not name:
                return False
            patterns = [
                rf'\b{re.escape(name)}\'s\b',
                rf'\b{re.escape(name)}\b',
                rf'\b{re.escape(name.lower())}\b'
            ]
            return any(re.search(pattern, text) for pattern in patterns)

        # 检查所有名字形式
        for key in self.NAME_KEYS:
            if check_name_existence(self.get_name(key)):
                return True
        # 检查别名
        return any(check_name_existence(alias) for alias in self.alias)

    def replace(self, text: str, new_name: str, lang: str) -> str:
        """替换文本中的角色名称"""
        text_processor = ChineseTextProcessor() if lang == "Chinese" else EnglishTextProcessor()
        
        # 处理别名
        for alias in self.alias:
            if not alias:
                continue
            old_name = re.sub(r'\s+', '', alias) if "-" in alias else alias
            text = text_processor.replace_name(old_name, new_name, text)

        # 处理标准名称
        for key in self.NAME_KEYS:
            old_name = self.get_name(key)
            if old_name:
                text = text_processor.replace_name(old_name, new_name, text)

        return text

    def load_from_dict(self, data: dict) -> None:
        """从字典加载角色数据
        
        Args:
            data: 包含角色信息的字典
        """
        self.first = data.get('first', '')
        self.last = data.get('last', '')
        self.full = data.get('full', '')
        self.full_revert = data.get('full_revert', '')
        self.tag = data.get('tag', '')
        self.alias = data.get('alias', [])

class TextProcessor:
    """文本处理的基类"""
    def replace_name(self, old_name: str, new_name: str, text: str) -> str:
        raise NotImplementedError

class EnglishTextProcessor(TextProcessor):
    """英文文本处理器"""
    def replace_name(self, old_name: str, new_name: str, text: str) -> str:
        base_forms = [old_name, old_name.lower(), old_name.upper()]
        
        for old in base_forms:
            patterns = [
                (rf'\b(\w+-)?{re.escape(old)}(-\w+[?!.~]*)?\b', new_name),
                (rf'\b{re.escape(old)}\'s\b', f"{new_name}'s"),
                (rf'\b{re.escape(old)}s\b', f"{new_name}'s"),
                (rf'\b\.*{re.escape(old)}\.+\b', new_name),
                (rf'\b\.+{re.escape(old)}~\.+\b', f"{new_name}~")
            ]
            
            for pattern, replacement in patterns:
                text = re.sub(pattern, replacement, text)
        return text

class ChineseTextProcessor(TextProcessor):
    """中文文本处理器"""
    def replace_name(self, old_name: str, new_name: str, text: str) -> str:
        return text.replace(old_name, new_name)

class CharacterManager:
    """角色管理类"""
    def __init__(self):
        self.characters = {}

    @staticmethod
    def load_characters(yaml_path: str) -> Dict[str, Character]:
        """从YAML文件加载角色
        
        Args:
            yaml_path: YAML文件路径
            
        Returns:
            角色字典
        """
        return load_characters_from_yaml_file(yaml_path)

    def set_characters(self, characters: Dict[str, Character]) -> None:
        """设置角色字典
        
        Args:
            characters: 角色字典
        """
        self.characters = characters

    @staticmethod
    def load_name_list(file_path: str) -> List[str]:
        """从YAML文件加载名字列表"""
        if not os.path.exists(file_path):
            logger.warning(f'File {file_path} does not exist')
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as stream:
                return yaml.safe_load(stream) or []
        except yaml.YAMLError as e:
            logger.error(f'Error loading name list: {e}')
            return []

    @staticmethod
    def get_whitelist(characters: Dict[str, Character]) -> Dict[str, str]:
        """获取角色名称的白名单"""
        whitelist = {}
        for character in characters.values():
            # 添加标准名称形式
            for key in Character.NAME_KEYS:
                name = getattr(character, key, '')
                if name:
                    whitelist[name] = name
            
            # 添加别名
            for alias in character.alias:
                if alias:
                    whitelist[alias] = alias
                    
        return whitelist

    @staticmethod
    def find_characters_hanlp(text: str, white_list: Dict[str, str]) -> List[str]:
        """使用 HanLP 查找文本中的人名
        
        Args:
            text: 要分析的文本
            white_list: 人名白名单字典
            
        Returns:
            找到的人名列表
        """
        try:
            import hanlp
        except ImportError:
            logger.error("HanLP not installed. Please install it first.")
            return []

        try:
            # 初始化 HanLP
            recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)
            
            # 使用 HanLP 进行命名实体识别
            entities = recognizer(text)
            
            # 收集所有人名
            characters = []
            for entity in entities:
                if entity[1] == 'PERSON':  # 如果是人名实体
                    name = entity[0]
                    # 检查是否在白名单中
                    if name in white_list:
                        characters.append(name)
            
            return list(set(characters))  # 去重返回
            
        except Exception as e:
            logger.error(f"Error in HanLP processing: {str(e)}")
            return []

class NameProcessor:
    """名字处理工具类"""
    @staticmethod
    def find_characters_nlp(text: str) -> List[str]:
        """使用spaCy进行英文命名实体识别"""
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        person_names = []
        current_person = []
        
        for token in doc:
            if token.ent_type_ == "PERSON":
                current_person.append(token.text)
            elif current_person:
                person_names.append(" ".join(current_person))
                current_person = []
                
        if current_person:
            person_names.append(" ".join(current_person))
            
        return list(set(person_names))

    @staticmethod
    def find_characters_hanlp(text: str, white_list: Dict[str, str]) -> List[str]:
        """使用HanLP进行中文命名实体识别"""
        HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
        ner = HanLP['ner/msra']
        ner.dict_whitelist = white_list
        
        doc = HanLP(text.splitlines(), tasks='ner/msra').to_dict()
        return list({word[0] for line in doc['ner/msra'] 
                    for word in line if word[1] == 'PERSON'})

def compare_names(name1: str, name2: str) -> bool:
    """比较两个名字是否相同"""
    if not (name1 and name2):
        return False
        
    name1 = name1.lower()
    name2 = name2.lower()
    
    if name1 == name2:
        return True
        
    if "-" in name2:
        return compare_names(
            name1.split('-')[0].strip(),
            name2.split('-')[0].strip()
        )
        
    return False

def replace_facial_features(text: str, color_hidden_str: str) -> str:
    """替换面部特征描述"""
    colors = [
        "red", "orange", "yellow", "green", "blue", "indigo", 
        "violet", "purple", "pink", "brown", "black", "white",
        "gray", "silver", "gold", "raven", "crimson", "beaujolais",
        "cerulean", "sakura", "mint", "ginger"
    ]
    
    for color in colors:
        for feature in [" eyes", " hair", "-haired", " head", " strand", " strands"]:
            pattern = rf"{color}\{feature}"
            text = re.sub(pattern, f"{color_hidden_str}{feature}", text, flags=re.IGNORECASE)
            # 处理首字母大写的情况
            pattern = rf"{color.capitalize()}{feature}"
            text = re.sub(pattern, f"{color_hidden_str}{feature}", text)
    
    text = text.replace("sharp teeth", "teeth")
    text = text.replace("Sharp teeth", "Teeth")
    
    for word in ["blonde", "blond", "blondish", "blondness", "brunette"]:
        for pattern in [rf'\b{word}\b', rf'\b{word.capitalize()}\b']:
            text = re.sub(pattern, color_hidden_str, text)
    
    return text

def load_characters_from_yaml_file(file_path: str) -> dict:
    """Load character definitions from a YAML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        characters = {}
        for char_data in data:
            # 使用 full 名称作为键
            full_name = char_data.get('full')
            if not full_name:
                continue
                
            character = Character()
            character.load_from_dict(char_data)
            characters[full_name] = character
            
        return characters
        
    except Exception as e:
        logger.error(f"Error loading characters from {file_path}: {str(e)}")
        return {}

def load_name_list_from_yaml_file(file_path: str) -> List[str]:
    """Load a list of names from a YAML file
    
    Args:
        file_path: Path to the YAML file containing the name list
        
    Returns:
        List of names from the YAML file
    """
    if not os.path.exists(file_path):
        logger.warning(f'File {file_path} does not exist')
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as stream:
            return yaml.safe_load(stream) or []
    except yaml.YAMLError as e:
        logger.error(f'Error loading name list from {file_path}: {e}')
        return []

def simple_text_replace(text: str, old: str, new: str, language: str = "English") -> str:
    """简单的文本替换函数
    
    Args:
        text: 要处理的文本
        old: 要替换的旧文本
        new: 新文本
        language: 语言，默认为英语
        
    Returns:
        替换后的文本
    """
    if not old or not text:
        return text
        
    if language == "English":
        # 英文需要考虑单词边界
        pattern = rf'\b{re.escape(old)}\b'
        return re.sub(pattern, new, text)
    else:
        # 中文直接替换
        return text.replace(old, new)

# 确保这些是模块级别的导出
__all__ = [
    'Character',
    'CharacterManager',
    'TextProcessor',
    'EnglishTextProcessor',
    'ChineseTextProcessor',
    'compare_names',
    'replace_facial_features',
    'load_characters_from_yaml_file',
    'load_name_list_from_yaml_file',
    'find_characters_hanlp',
    'simple_text_replace'  # 添加新函数到导出列表
]

