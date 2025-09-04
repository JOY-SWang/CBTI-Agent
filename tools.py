import json
import datetime
import inspect

from camel.toolkits import FunctionTool
from database import save_emotion_log, find_resources

def record_emotion_tool(user_id: int, emotion: str, intensity: int, note: str = None) -> str:
    """
    记录用户的情绪日志。
    Args:
        user_id (int): 用户ID。
        emotion (str): 情绪描述（如：焦虑、平静、喜悦）。
        intensity (int): 情绪强度（1-10分）。
        note (str, optional): 情绪备注。
    Returns:
        str: 操作结果的JSON字符串。
    """
    # 这里可以添加参数校验，例如强度是否在1-10之间
    if not (1 <= intensity <= 10):
        return json.dumps({"status": "error", "message": "情绪强度必须在1到10之间。"})
        
    success = save_emotion_log(user_id, emotion, intensity, note)
    if success:
        return json.dumps({"status": "success", "message": "情绪记录成功！"})
    else:
        return json.dumps({"status": "error", "message": "情绪记录失败，请稍后再试。"})

def get_resources_tool(tag: str = None) -> str:
    """
    根据标签查询心理健康资源。
    Args:
        tag (str, optional): 资源标签（如：放松、焦虑管理）。
    Returns:
        str: 匹配资源的JSON字符串列表。
    """
    resources = find_resources(tag)
    if not resources:
        return json.dumps({"status": "success", "resources": [], "message": f"未找到与标签'{tag}'相关的资源。"})
    
    return json.dumps({"status": "success", "resources": resources})

# 将工具函数封装为 FunctionTool
EmotionRecorderTool = FunctionTool(record_emotion_tool)
ResourceFinderTool = FunctionTool(get_resources_tool)

# 打印工具的签名，方便调试
print("EmotionRecorderTool Signature:", inspect.signature(record_emotion_tool))
print("ResourceFinderTool Signature:", inspect.signature(get_resources_tool))