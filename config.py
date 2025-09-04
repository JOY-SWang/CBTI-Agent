import os

# API 配置
# 请将你的API Key替换为实际的，或者通过环境变量加载
# os.getenv("MODEL_API_KEY")
API_KEY = "ms-20fdc728-c981-4934-8980-99ddd61dd0b1"
MODEL_URL = 'https://api-inference.modelscope.cn/v1/'
MODEL_TYPE = "Qwen/Qwen2.5-72B-Instruct"

# 数据库配置
DB_FILE = '/data1/cyjx/agent/mental_health_assistant/data/mental_health_agent.db'

# 用户ID（示例，实际应用中应由登录系统动态生成）
TEST_USER_ID = 1

# 情绪日志工具的参数
EMOTION_INTENSITY_RANGE = (1, 10)