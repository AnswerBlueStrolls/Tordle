import os
import yaml

class FandomConfig:
    SUPPORTED_LANGUAGES = ["English", "Chinese"]  # 支持的语言列表
    SUPPORTED_FANDOMS = {'ensemble stars': 'ensemble_stars'}
    def __init__(self, config_file=""):
        self.config = {}
        self.base_path = ""
        if config_file != "":
            self.load_from_file(config_file)

    @classmethod
    def create_from_web(cls, fandom, language="English"):
        """从网页参数创建配置"""
        instance = cls()
        instance.base_path = os.path.join(os.path.dirname(__file__), '..', 'metadata', cls.SUPPORTED_FANDOMS[fandom])
        instance.config = {
            "language": language,
            "web_mode": True,
            "debug": False,
            "read_mode": False,
            "history": False,
            "db_name": os.path.join(instance.base_path, "ao3.db"),  # 数据库文件名
            "table_name": "fanfics_raw",
            "fanfic_index": 21,
            "limit": 5300  # 默认文本长度限制
        }
    
        return instance

    @property
    def supported_languages(self):
        """获取支持的语言列表"""
        return self.SUPPORTED_LANGUAGES

    def load_from_file(self, config_file):
        if not config_file:
            raise ValueError("Config file path is empty")
        
        self.base_path = os.path.dirname(config_file)
        self.config = yaml.safe_load(open(config_file))
        self.config["db_name"] = os.path.join(self.base_path, self.config["db_name"])

    def get(self, key, default=None):
        return self.config.get(key, default)

    @property
    def debug_mode(self):
        return self.config.get("debug", False)

    @property
    def read_mode(self):
        return self.config.get("read_mode", False)

    @property
    def web_mode(self):
        return self.config.get("web_mode", False)

    @property
    def language(self):
        return self.config.get("language", "English")

    @property
    def history(self):
        return self.config.get("history", False)

    @property
    def db_name(self):
        return self.config.get("db_name")

    def get_character_file(self):
        if self.language == "Chinese":
            return os.path.join(self.base_path, "characters_cn.yml")
        return os.path.join(self.base_path, "characters.yml")

    def get_special_names_file(self):
        if self.language == "Chinese":
            return os.path.join(self.base_path, "special_names_cn.yml")
        return os.path.join(self.base_path, "special_names.yml")

    def get_exception_names_file(self):
        return os.path.join(self.base_path, "exception_names.yml")

    def get_remove_names_file(self):
        return os.path.join(self.base_path, "remove_names_cn.yml")
