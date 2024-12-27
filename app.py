import logging
import utils.log_config  # 确保日志配置被加载
from flask import Flask, render_template, request, jsonify
import lottery
# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


app = Flask(__name__)

@app.route('/')
def index():
    # 定义fandom列表
    options = ['none', 'ensemble stars', '选项2', '选项3', '选项4']
    logger.info(f"当前访问的用户 ID 是：{options}")
    return render_template('index.html', fandomoptions=options)


@app.route('/run', methods=['POST'])

def run_main():
    """
    Handle POST request to run main.py with parameters.
    """
    data = request.json  # Parse JSON data from frontend
    fandom = data.get('fandom', 'none')  # Default value
    workid = data.get('workid', '0')
    config = ''
    logger.info(f"fandom is {fandom}, workid {workid}")
    if fandom == 'ensemble stars':
        config = 'metadata/ensemble_stars/config.yml'
    # Call the main logic with provided parameters
    logger.info(f'call with config {config}, workid: "{workid}"')
    try:
        intid = int(workid)
    except ValueError:
        intid = 0
    result, mappings, all_characters = lottery.web_lottery(config, intid)
    return jsonify({'text': result, 'mappings': mappings, 'all_characters': all_characters})


if __name__ == '__main__':
    try:
        app.run(
            host='127.0.0.1',
            port=8081,
            debug=True)
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")

