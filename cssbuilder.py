import os
import json


ROOT_PATH = "./projects/"
class CssBuilder:
    @staticmethod
    def getHistoryFile(project_name):
        file_path = os.path.join(ROOT_PATH,project_name,"history.json")
        with open(file_path,"r") as file:
            return json.load(file)

    @staticmethod
    def getStructureFile(project_name):
        file_path = os.path.join(ROOT_PATH,project_name,"structure.json")
        with open(file_path,"r") as file:
            return json.load(file)
    
    @staticmethod
    def build(project_name):
        """根据structure.json生成sheng-color.css"""
        
        # 读取structure数据
        css_path = os.path.join(ROOT_PATH,project_name,"sheng-color.css")
        structure = CssBuilder.getStructureFile(project_name)

        if not structure:
            return False
        
        # 生成CSS内容
        css_content = '/* 自动生成的颜色样式表 - 请勿手动修改 */\n\n'
        # 确定选择器 (.class 或 #id)
        #selector = f".{item['value']}" if item['type'] == 'class' else f"#{item['value']}"
        
        # 初始化CSS内容列表
        css_lines = []

        # 遍历对象中的每个选择器
        for selector, styles in structure["value"].items():
            # 添加选择器和开括号
            css_lines.append(f"{selector} {{")
            # 遍历每个样式属性
            for prop, value in styles.items():
                # 添加属性和值（缩进4个空格）
                css_lines.append(f"    {prop}: {value};")
            # 添加闭括号
            css_lines.append("}")
        
        css_content += "\n".join(css_lines)
                
        # 确定CSS属性
        """
        if item['target'] == 'background':
            css_property = 'background-color'
        elif item['target'] == 'font':
            css_property = 'color'
        elif item['target'] == 'border':
            css_property = 'border-color'
        else:
            continue  # 跳过未知目标
        """
        
        # 添加CSS规则
        #css_content += f"{final_head} {{\n  {css_property}: {item['colorValue']};\n}}\n\n"
                
        # 保存CSS文件
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        return True


    @staticmethod
    def appendStructure(project_name:str,draw_data:dict,UNDO=False):
        """
        draw_data = {
                'which': request.form.get('which'),  # 'class' 或 'id'
                'label': request.form.get('label'),  # 类名或ID
                'target': request.form.get('target'),  # 'background' 等
                'value': request.form.get('value'),  # 颜色值
                'state': request.form.get('state'), #default focues hover 等
                #'index': len(structure)  # 索引为当前长度（最后一位）
            }
        """
        structureObj = CssBuilder.getStructureFile(project_name)
        structure_path = os.path.join(ROOT_PATH,project_name,"structure.json")
        print("draw_data",draw_data,"UNDO",UNDO)
        if draw_data:
        
            which = draw_data["which"]
            label = draw_data["label"]
            target = draw_data["target"]
            value = draw_data["value"]
            state = draw_data["state"]

            with open(structure_path,"w") as file:
                key_head = "." if which == "class" else "#"
                key_head += label

                #if label not in  structureObj["key"][state]:
                #    structureObj["key"][state].append(key_head)
                
                final_key = "{0}:{1}".format(key_head,state)
                if state == "default":
                    final_key = key_head
                
                if final_key not in structureObj["value"]:
                    structureObj["value"][final_key] = {}

                structureObj["value"][final_key][target] = value

                

                json.dump(structureObj,file,indent=2)
        else:
            with open(structure_path,"w") as file:
                pre_data = {
                    "value": {}
                }
                json.dump(pre_data,file,indent=2)
            CssBuilder.build(project_name)

        if not UNDO:
            CssBuilder.appendHistory(project_name,draw_data)

    @staticmethod
    def appendHistory(project_name,draw_data):
        history_obj = CssBuilder.getHistoryFile(project_name)
        history_path = os.path.join(ROOT_PATH,project_name,"history.json")
        with open(history_path,"w") as file:
            history_obj.append(draw_data)
            json.dump(history_obj,file,indent=2)
    
    @staticmethod
    def buildStructureFromHistory(project_name):
        history_path = os.path.join(ROOT_PATH,project_name,"history.json")
        with open(history_path,"r") as file:
            history_obj = json.load(file)
            if len(history_obj) > 0:
                for raw_data in history_obj:
                    CssBuilder.appendStructure(project_name,raw_data,True)
            else:
                CssBuilder.appendStructure(project_name,{},True)

    @staticmethod
    def undo(project_name):
        history_obj = CssBuilder.getHistoryFile(project_name)
        if history_obj:
            history_obj.pop()
            history_path = os.path.join(ROOT_PATH,project_name,"history.json")
            with open(history_path,"w") as file:
                json.dump(history_obj,file,indent=2)
            CssBuilder.buildStructureFromHistory(project_name)
        else: 
            raise Exception("无法再撤回了")
        
        


        
         

        




