from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
import os
import json
import shutil
import base64
import random
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from generator import AIGenerator
from cssbuilder import CssBuilder
app = Flask(__name__)
# 允许所有来源的跨域请求（开发环境适用）
CORS(app, resources={r"/*": {"origins": "*"}})  


# 配置文件路径和设置
CONFIG_FILE = 'config.json'
ROOT_PATH = './projects'  # 项目根目录

# 确保项目根目录存在
os.makedirs(ROOT_PATH, exist_ok=True)
CONFIG_OBJ = {}
class ConfigManager:
    @staticmethod
    def load_config():
        """加载配置文件"""
        print("load")
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                obj = json.loads(f.read())
                f.close()
                return obj
        return {
            'root_path': ROOT_PATH,
            'setting': {
                'which': 'class',
                'target': 'background',
                'filter': 'sheng'
            },
            'key': [],
            'color': [],
            'file': []
        }

    @staticmethod
    def save_config(config):
        """保存配置文件"""
        CONFIG_OBJ = config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
            f.close()

CONFIG_OBJ = ConfigManager.load_config()

def add_link_to_html(html_path, href, rel='stylesheet', attrs=None):
    """
    向HTML文件中添加link标签
    
    :param html_path: HTML文件路径
    :param href: link标签的href属性值
    :param rel: link标签的rel属性，默认为'stylesheet'
    :param attrs: 额外的标签属性字典（可选）
    """
    # 读取HTML文件
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # 创建link标签
    link_attrs = {'rel': rel, 'href': href}
    
    # 如果有额外属性，则添加
    if attrs:
        link_attrs.update(attrs)
    
    new_link = soup.new_tag('link', **link_attrs)
    
    # 将link标签添加到head标签中
    soup.head.append(new_link)
    
    # 写回HTML文件
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def get_project_path(project_name):
    """获取项目路径"""
    return os.path.join(ROOT_PATH, project_name)


def get_structure_path(project_name):
    """获取structure.json文件路径"""
    return os.path.join(get_project_path(project_name), 'structure.json')

def get_history_path(project_name):
    return os.path.join(get_project_path(project_name), 'history.json')

def get_css_path(project_name):
    """获取生成的CSS文件路径"""
    return os.path.join(get_project_path(project_name), 'sheng-color.css')


def init_project_files(project_name):
    """初始化项目所需的文件（structure.json和CSS）"""
    structure_path = get_structure_path(project_name)
    history_path = get_history_path(project_name)
    if not os.path.exists(structure_path):
        with open(structure_path, 'w') as f:
            defaultObj = {
                "key":{
                    "default": [],
                    "focus": [],
                    "hover": []
                },
                "value":{
                    #".class1:hover" : {
                    #    "background": "#123123",
                    #    "border": "solid 1px #123123"
                    #}
                }
            }
            json.dump({}, f, indent=2)
    
    # history.json文件
    if not os.path.exists(history_path, 'w'):
        with open(structure_path, 'w') as f:
            defaultObj = []
            json.dump({}, f, indent=2)

    # 确保CSS文件存在
    css_path = get_css_path(project_name)
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write('/* 自动生成的颜色样式表 */\n')


def generate_css_from_structure(project_name):
    """根据structure.json生成sheng-color.css"""
    structure_path = get_structure_path(project_name)
    css_path = get_css_path(project_name)
    
    if not os.path.exists(structure_path):
        return False
    
    # 读取structure数据
    with open(structure_path, 'r') as f:
        structure = json.load(f)
    
    # 生成CSS内容
    css_content = '/* 自动生成的颜色样式表 - 请勿手动修改 */\n\n'
    for item in structure:
        # 确定选择器 (.class 或 #id)
        selector = f".{item['value']}" if item['type'] == 'class' else f"#{item['value']}"
        
        # 确定CSS属性
        if item['target'] == 'background':
            css_property = 'background-color'
        elif item['target'] == 'font':
            css_property = 'color'
        elif item['target'] == 'border':
            css_property = 'border-color'
        else:
            continue  # 跳过未知目标
        
        # 添加CSS规则
        css_content += f"{selector} {{\n  {css_property}: {item['colorValue']};\n}}\n\n"
    
    # 保存CSS文件
    with open(css_path, 'w') as f:
        f.write(css_content)
    
    return True

@app.route('/config', methods=['GET'])
def get_config():
    """获取完整的配置信息"""
    try:
        config = CONFIG_OBJ
        return jsonify({
            'status': 'ok',
            'data': config  # 返回完整配置数据
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取配置失败：{str(e)}'
        }), 500

@app.route('/config', methods=['POST'])
def handle_config():
    config = CONFIG_OBJ
    part = request.form.get('part')

    try:
        if part == 'setting':
            config['setting'] = json.loads(request.form.get('value', '{}'))
        elif part == 'color':
            key = request.form.get('key')
            value = json.loads(request.form.get('value', '{}'))
            
            # 查找颜色组并添加新颜色
            for color_group in config['color']:
                if key in color_group:
                    color_group[key].append(value)
                    break
        elif part == 'color_folder':
            new_folder = request.form.get('value')
            config['key'].append(new_folder)
            config['color'].append({new_folder: []})

        ConfigManager.save_config(config)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/project', methods=['POST'])
def handle_project():
    method = request.form.get('method')
    name = request.form.get('name')

    try:
        if method == 'delete':
            project_path = get_project_path(name)
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            
            # 更新配置中的项目列表
            config = CONFIG_OBJ
            if name in config['file']:
                config['file'].remove(name)
                ConfigManager.save_config(config)

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '未上传文件'})

    file = request.files['file']
    filename = secure_filename(file.filename)
    project_name = os.path.splitext(filename)[0]

    try:
        # 创建项目目录
        project_path = get_project_path(project_name)
        os.makedirs(project_path, exist_ok=True)

        # 保存上传的HTML文件
        file_path = os.path.join(project_path, filename)
        file.save(file_path)

        href = "/style/" + project_name + "/color"
        add_link_to_html(file_path,href)

        # 初始化structure.json和CSS文件
        init_project_files(project_name)

        # 更新配置中的项目列表
        config = CONFIG_OBJ
        if project_name not in config['file']:
            config['file'].append(project_name)
            ConfigManager.save_config(config)

        return jsonify({'status': 'ok', 'message': '文件上传成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/ai_generate', methods=['POST'])
def ai_generate():
    try:
        message = request.form.get("message")
        message += "\n" + ",".join(CONFIG_OBJ["key"]) + "\n上面为已有的folder_name请不要重名"
        #后续可以引入其他的ai进行生成
        #file = request.files['file']
        ai_response = AIGenerator.generate(message)
        # 模拟AI生成颜色方案
        folder_name = ai_response["folder_name"]
        # 生成示例颜色
        colors = ai_response["color"]
        # 更新配置
        """
        config = ConfigManager.load_config()
        if folder_name not in config['file']:
            config['file'].append(folder_name)
            ConfigManager.save_config(config)
        """
        
        return jsonify({
            'status': 'ok', 
            'folder_name': folder_name,
            'color': colors
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/draw', methods=['POST'])
def handle_draw():
    method = request.form.get('method')
    project_name = request.form.get('project_name')  # 获取当前操作的项目名

    if not project_name:
        return jsonify({'status': 'error', 'message': '未指定项目名称'})

    try:
        if method == 'action':
            """整合在cssbuilder中"""
            # 处理绘图操作 - 新增记录到structure.json
            structure_path = get_structure_path(project_name)
            
            # 读取现有结构数据
            with open(structure_path, 'r') as f:
                structure = json.load(f)
            
            # 获取绘图参数
            draw_data = {
                'which': request.form.get('which'),  # 'class' 或 'id'
                'label': request.form.get('label'),  # 类名或ID
                'target': request.form.get('target'),  # 'background' 等
                'value': request.form.get('value'),  # 颜色值
                #'state': request.form.get('state'), #focues hover 等
                #'index': len(structure)  # 索引为当前长度（最后一位）
            }
            
            
            # 添加新记录
            structure.append(draw_data)
            
            # 保存更新后的结构
            with open(structure_path, 'w') as f:
                json.dump(structure, f, indent=2)
            
            # 重新生成CSS文件
            generate_css_from_structure(project_name)

        elif method == 'undo':
            # 撤销操作 - 删除首行记录
            structure_path = get_structure_path(project_name)
            
            with open(structure_path, 'r') as f:
                structure = json.load(f)
            
            # 如果有记录则删除第一条
            if structure:
                structure.pop(-1)
                
                # 更新索引（重新编号）
                for i, item in enumerate(structure):
                    item['index'] = i
                
                # 保存更新
                with open(structure_path, 'w') as f:
                    json.dump(structure, f, indent=2)
                
                # 重新生成CSS文件
                generate_css_from_structure(project_name)

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def get_root_path():
    """从配置文件获取项目根目录，默认使用ROOT_PATH"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('root_path', ROOT_PATH)
    except (FileNotFoundError, json.JSONDecodeError):
        return ROOT_PATH

@app.route('/assets/<file_name>', methods=['GET'])
def get_assest_file(file_name):
    ASSEST_PATH = "./dist/assets"
    FINAL_PATH = os.path.join(ASSEST_PATH,file_name)

    file_content  = ""
    with open(FINAL_PATH,"r",encoding="utf-8") as file:
        file_content = file.read()
        file.close()

    response = make_response(file_content)
    file_type = str(file_name).split(".")[1]
    if file_type == "css":
        response.headers['Content-Type'] = 'text/css; charset=utf-8'
    elif file_type == "js":
        response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
    return response

@app.route("/index", methods=["GET"])
def get_index_html():
    INDEX_PATH = "./dist/index.html"
    html_content = ""
    with open(INDEX_PATH,"r") as file:
        html_content = file.read()
        file.close()

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/project/<project_name>/file', methods=['GET'])
def get_project_file(project_name):
    """
    根据项目名称返回对应的HTML文件内容
    路由格式: /project/{project_name}/file
    """
    root_path = get_root_path()
    project_path = os.path.join(root_path, project_name)
    
    # 验证项目是否存在
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        abort(404, description=f"项目 '{project_name}' 不存在")
    
    # 查找项目目录中的HTML文件（默认找与项目名相同的HTML文件）
    html_filename = f"{project_name}.html"
    html_path = os.path.join(project_path, html_filename)
    
    # 如果找不到默认HTML文件，尝试查找目录中第一个HTML文件
    if not os.path.exists(html_path):
        html_files = [f for f in os.listdir(project_path) if f.endswith('.html')]
        if not html_files:
            abort(404, description=f"项目 '{project_name}' 中未找到HTML文件")
        html_path = os.path.join(project_path, html_files[0])
    
    # 读取并返回HTML内容
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建响应，设置正确的Content-Type
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    except Exception as e:
        abort(500, description=f"读取文件失败: {str(e)}")

@app.route('/style/<project_name>/color')
def get_color_style(project_name):
    COLOR_FILE_PATH = "./projects/{}/sheng-color.css".format(project_name)
    content = ""
    with open(COLOR_FILE_PATH,"r") as file:
        content = file.read()
    
    response = make_response(content)
    response.headers['Content-Type'] = 'text/css; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(debug=True,port=8080)
    