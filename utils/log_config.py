# log_config.py
import logging

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 初始化日志配置
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,          # 设置全局日志级别
        format=LOG_FORMAT,            # 设置日志格式
        handlers=[
            logging.FileHandler("app.log"),  # 日志输出到文件
            logging.StreamHandler()          # 日志同时输出到控制台
        ]
    )

# 运行初始化
setup_logger()
