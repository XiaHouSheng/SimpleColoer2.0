import os
import json


ROOT_PATH = "./projects/"

class CssBuilder:
    @staticmethod
    def getHistoryFile(project_name):
        file = open(ROOT_PATH + project_name + "/history.json","r")
        return json.load(file)

    @staticmethod
    def getStructureFile(project_name):
        file = open(ROOT_PATH + project_name + "/structure.json","r")
        return json.load(file)

    @staticmethod
    def buildStructure(project_name:str,draw_data:dict):
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

        which = draw_data["which"]
        label = draw_data["label"]
        target = draw_data["target"]
        value = draw_data["value"]
        state = draw_data["state"]

        with open(ROOT_PATH + project_name + "/structure.json") as file:
            key_head = "." if which == "class" else "#"
            key_head += label

            if label not in  structureObj["key"][state]:
                structureObj["key"][state].append(key_head)
                
            final_key = "{0}:{1}".format(key_head,state)
            structureObj["value"][final_key][target] = value

            json.dump(file,structureObj,indent=2)
        
        CssBuilder.appendHistory(key_head,final_key,target,value)

    @staticmethod
    def appendHistory(project_name,draw_data):
        history_obj = CssBuilder.getHistoryFile(project_name)
        with open(ROOT_PATH + project_name + "/history.json","w") as file:
            history_obj.append(draw_data)
            json.dump(history_obj,file,indent=2)
    
    @staticmethod
    def undo(project_name):
        history_obj = CssBuilder.getHistoryFile(project_name)
        #structure_obj = CssBuilder.getStructureFile(project_name)
        if history_obj:
            #undo将倒数前两个存下，倒数第一个删除
            """
            存倒数第二个，用于执行，若直接进行history-》structure-》css操作
            效率太低，并且history不能存储所有的action数据，设定最大length，
            """
            history_obj.pop()
            last_action = history_obj[-1]
            with open(ROOT_PATH + project_name + "/history.json","w") as file:
                json.dump(history_obj,file,indent=2)
            CssBuilder.buildStructure(project_name,last_action)
        else:
            pass




        
         

        




