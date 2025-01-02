import logging
import utils.log_config  # 确保日志配置被加载
from flask import Flask, render_template, request, jsonify
import lottery
from utils.fandom_config import FandomConfig
import os
# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the main page.
    """
    fandoms = list(FandomConfig.SUPPORTED_FANDOMS.keys())
    supported_languages = FandomConfig.SUPPORTED_LANGUAGES

    return render_template('index.html', 
                         fandomoptions=fandoms,
                         supported_languages=supported_languages)  # 传递语言列表到模板


@app.route('/run', methods=['POST'])
def run_main():
    """
    Handle POST request to run main.py with parameters.
    """
    data = request.json  # Parse JSON data from frontend
    fandom = data.get('fandom', 'none')  # Default value
    workid = data.get('workid', '0')
    language = data.get('language', 'English')
    text_length = data.get('text_length', '-1')  # 新增文章长度参数，默认为全文
    config = ''
    
    logger.info(f"fandom is {fandom}, workid {workid}, language {language}, text_length {text_length}")
    
    if fandom == 'ensemble stars':
        config = FandomConfig.create_from_web(fandom, language)
    
    # Call the main logic with provided parameters
    logger.info(f'call with config {config}, workid: "{workid}"')
    try:
        inttext_length = int(text_length)
        intid = int(workid)
    except ValueError:
        intid = 0
        inttext_length = -1
        
    result, mappings, all_characters = lottery.web_lottery(fandom, language, intid, inttext_length)  # 添加 text_length 参数
    return jsonify({
        'text': result, 
        'mappings': mappings, 
        'all_characters': ['--'] + sorted(all_characters)
    })


if __name__ == '__main__':
    try:
        app.run(
            host='127.0.0.1',
            port=8081,
            debug=True)
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")

