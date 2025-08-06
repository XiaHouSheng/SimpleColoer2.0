

SimpleColor 2.0 是一个基于AI的网站配色方案生成与管理工具，能够帮助开发者快速生成符合需求的配色方案，并自动构建对应的CSS样式文件，简化前端开发中的色彩管理流程。

**当前处于开发阶段**
## 开发计划
- **border属性的solid与radius添加**
- **导出Css文件**
- **变量命名法，调整css**



## 功能特点

- **AI配色方案生成**：通过AI根据网站类型、风格等需求生成专业配色方案
- **配色方案管理**：支持创建、删除和管理多个配色方案
- **CSS自动生成**：根据配色方案自动生成对应的CSS样式文件
- **项目管理**：支持上传HTML文件，为不同项目维护独立的配色方案
- **操作历史记录**：支持操作撤销功能，方便调整配色方案

## 目录结构

```
SimpleColor2.0/
├── generator.py       # AI配色方案生成模块
├── cssbuilder.py      # CSS文件生成与管理模块
├── server.py          # 后端服务与API接口
├── key.txt            # API密钥文件（需自行创建）
├── config.json        # 配置文件
├── projects/          # 项目存储目录
└── .gitignore         # Git忽略文件
```

## 环境要求

- Python 3.6+
- 依赖库：flask, flask-cors, openai, beautifulsoup4

## 安装与使用

1. 克隆项目到本地
```bash
git clone <项目仓库地址>
cd SimpleColor2.0
```

2. 安装依赖
```bash
pip install flask flask-cors openai beautifulsoup4
```

3. 配置API密钥
在项目根目录创建`key.txt`文件，填入你的API密钥：
```
your_api_key_here
```

4. 启动服务
```bash
python server.py
```

5. 访问服务
打开浏览器访问`http://localhost:5000`（默认Flask端口）

## 主要模块说明

### generator.py
AI配色方案生成模块，通过调用DeepSeek API生成符合要求的配色方案，支持根据主题色生成变体或随机生成相关色系。

### cssbuilder.py
CSS构建模块，负责：
- 管理配色方案的结构数据
- 记录操作历史
- 根据结构数据生成CSS文件
- 支持撤销操作

### server.py
Flask后端服务，提供RESTful API接口，包括：
- 配置管理
- 项目管理
- 文件上传
- AI配色生成
- 绘图操作处理

## API接口说明

- `GET /config`：获取系统配置
- `POST /config`：更新系统配置
- `POST /project`：项目管理（删除等操作）
- `POST /file`：上传HTML文件创建新项目
- `POST /ai_generate`：生成AI配色方案
- `POST /draw`：处理绘图操作

## 注意事项

- `key.txt`和`config.json`已加入.gitignore，不会被提交到版本控制
- 项目数据存储在`projects/`目录下
- 生成的CSS文件为`sheng-color.css`，自动关联到上传的HTML文件

## 许可证

[MIT](LICENSE)
