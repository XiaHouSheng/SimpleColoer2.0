import json
from openai import OpenAI

with open("key.txt","r") as file:
    api_key = file.read()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

system_prompt = """
请你根据我提出的网站配色需求（如站点类型、明暗风格、主题色代码等），按照以下规范的JSON格式生成配色方案。若需求中包含“随机”字样，需注意：**并非完全无规律随机，而是在指定框架内随机——即基于1-2种核心色系（或由我指定的主题色），随机生成其明度、饱和度变体，或有限范围内的关联色（色相角差≤40°），确保整体仍符合集中性要求**：

{
  "folder_name": "xx组合",  // 文件夹名称，精准体现核心色系（如"青灰随机组合""暖橙变体搭配"），不超过7个字，需包含"随机"或"变体"体现特性
  "color": [
    {
      "title": "导航栏",  // 颜色应用位置，覆盖网站核心元素（如"侧边栏""卡片背景""标题文字""交互按钮""提示框"等，共10-12个），每个标题不超过4个字
      "content": "说明颜色与核心色系的关联（如基于#2C3E50的随机明度变体、主题色衍生的低饱和随机色），描述特点（如随机调整饱和度但保持统一明度基调）及适配场景，50-80字",
      "value": "#123456"  // 颜色代码（支持带透明度），随机范围严格限定在核心色系的明度（±30%）、饱和度（±20%）调整内，或关联色相范围内，避免跳出主色系框架
    }
  ]
}

请依据具体需求生成方案：若指定“随机”且提供主题色，所有颜色需从该主题色的变体中随机选取；若仅指定“随机”，则先确定1-2种核心色，再在其衍生范围内随机生成，确保90%颜色仍与核心色强关联，避免杂乱无章的“完全随机”。
"""

class AIGenerator:
    @staticmethod
    def generate(user_prompt = "给我一个高端大气的配色方案，主题色为蓝色"):
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        return json.loads(response.choices[0].message.content)