# import os
# import datetime
# import json

# from camel.messages import BaseMessage
# from camel.types import ModelPlatformType
# from camel.models import ModelFactory

# from config import API_KEY, MODEL_URL, MODEL_TYPE, TEST_USER_ID
# from database import (
#     setup_database, 
#     save_conversation_message, 
#     get_user_conversation_history,
#     get_db_connection
# )
# from agents import (
#     psych_assistant_sys_msg, 
#     crisis_evaluator_sys_msg,
#     crisis_handler_sys_msg,
#     MentalHealthAgent
# )
# from tools import EmotionRecorderTool, ResourceFinderTool

# def setup_agent_system():
#     """
#     初始化并设置整个Agent系统。
#     """
#     setup_database()

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT OR IGNORE INTO users (id, username, created_at) VALUES (?, ?, ?)", 
#                    (TEST_USER_ID, "Agent测试用户", datetime.datetime.now().isoformat()))
#     conn.commit()
#     conn.close()

#     model = ModelFactory.create(
#         model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
#         model_type=MODEL_TYPE,
#         url=MODEL_URL,
#         api_key=API_KEY
#     )
    
#     # 不同的 Agent 实例
#     main_agent = MentalHealthAgent(psych_assistant_sys_msg, model, tools=[EmotionRecorderTool, ResourceFinderTool], user_id=TEST_USER_ID)
#     crisis_evaluator_agent = MentalHealthAgent(crisis_evaluator_sys_msg, model, user_id=TEST_USER_ID)
#     crisis_handler_agent = MentalHealthAgent(crisis_handler_sys_msg, model, user_id=TEST_USER_ID)

#     return main_agent, crisis_evaluator_agent, crisis_handler_agent

# def run_multi_agent_flow(user_input: str, main_agent, crisis_evaluator_agent, crisis_handler_agent):
#     """
#     运行多 Agent 协作的对话流程。
#     """
#     print(f"\n用户输入: {user_input}")
    
#     # 1. 危机评估：由专门的 Agent 判断
#     crisis_check_prompt = BaseMessage.make_user_message(
#         role_name="用户",
#         content=f"请判断以下用户消息是否包含自伤、自杀或严重伤害他人的风险信号：{user_input}"
#     )
    
#     crisis_response = crisis_evaluator_agent.step(crisis_check_prompt)
#     is_crisis = crisis_response.msg.content.strip().lower()

#     # 记录危机检测结果到数据库
#     save_conversation_message(TEST_USER_ID, "crisis_check", is_crisis)

#     # 2. 根据判断结果分流
#     if is_crisis == "是":
#         print("危机检测结果: 是，进入紧急处理流程。")
#         crisis_prompt = BaseMessage.make_user_message(
#             role_name="用户",
#             content=f"用户表达了严重的危机情绪：{user_input}"
#         )
#         final_response = crisis_handler_agent.step(crisis_prompt)
#         response_content = final_response.msg.content
#     else:
#         print("危机检测结果: 否，进入正常对话流程。")
#         # 正常对话和工具调用
#         history = get_user_conversation_history(TEST_USER_ID)
#         combined_prompt = BaseMessage.make_user_message(
#             role_name="用户",
#             content=f"以下是之前的对话历史：\n{history}\n用户当前说：{user_input}"
#         )
        
#         response = main_agent.step(combined_prompt)
#         response_content = response.msg.content

#         # 检查是否有工具调用并处理
#         if response.info and 'tool_calls' in response.info:
#             tool_executed_message = ""
#             for tool_call in response.info['tool_calls']:
#                 tool_name = tool_call.tool_name
#                 args = tool_call.args
#                 print(f"Agent 意图调用工具: {tool_name}, 参数: {args}")

#                 if tool_name == EmotionRecorderTool.get_tool_name():
#                     tool_output_json = EmotionRecorderTool.run(**args)
#                 elif tool_name == ResourceFinderTool.get_tool_name():
#                     tool_output_json = ResourceFinderTool.run(**args)
#                 else:
#                     tool_output_json = json.dumps({"status": "error", "message": "未知工具"})

#                 tool_output = json.loads(tool_output_json)
#                 tool_executed_message += f"\n\n(工具执行结果: {tool_output['message'] if 'message' in tool_output else tool_output_json})"
            
#             response_content += tool_executed_message

#     # 保存对话并打印最终回复
#     save_conversation_message(TEST_USER_ID, "user", user_input)
#     save_conversation_message(TEST_USER_ID, "agent", response_content)
#     print(f"心理健康助手: {response_content}")

# if __name__ == "__main__":
#     main_agent, crisis_evaluator_agent, crisis_handler_agent = setup_agent_system()
    
#     print("\n--- 心理健康助手系统启动 ---")
#     print("你可以输入你的感受。尝试输入'我真的太绝望了，不想活了。'来测试危机干预。")
#     print("输入 '退出' 结束对话。")
    
#     while True:
#         user_input = input("\n> 你: ")
#         if user_input.lower() == '退出':
#             print("再见！祝你一切顺利。")
#             break
        
#         run_multi_agent_flow(user_input, main_agent, crisis_evaluator_agent, crisis_handler_agent)

import os
import datetime
import json

from camel.messages import BaseMessage
from camel.types import ModelPlatformType
from camel.models import ModelFactory

from config import API_KEY, MODEL_URL, MODEL_TYPE, TEST_USER_ID
from database import (
    setup_database, 
    save_conversation_message, 
    get_user_conversation_history,
    get_db_connection
)
from agents import (
    psych_assistant_sys_msg, 
    crisis_evaluator_sys_msg,
    crisis_handler_sys_msg,
    MentalHealthAgent
)
from tools import EmotionRecorderTool, ResourceFinderTool

def setup_agent_system():
    """
    初始化并设置整个Agent系统。
    """
    setup_database()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, created_at) VALUES (?, ?, ?)", 
                   (TEST_USER_ID, "Agent测试用户", datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=MODEL_TYPE,
        url=MODEL_URL,
        api_key=API_KEY
    )
    
    # 不同的 Agent 实例
    main_agent = MentalHealthAgent(psych_assistant_sys_msg, model, tools=[EmotionRecorderTool, ResourceFinderTool], user_id=TEST_USER_ID)
    crisis_evaluator_agent = MentalHealthAgent(crisis_evaluator_sys_msg, model, user_id=TEST_USER_ID)
    crisis_handler_agent = MentalHealthAgent(crisis_handler_sys_msg, model, user_id=TEST_USER_ID)

    return main_agent, crisis_evaluator_agent, crisis_handler_agent

def run_multi_agent_flow(user_input: str, main_agent, crisis_evaluator_agent, crisis_handler_agent):
    """
    运行多 Agent 协作的对话流程。
    """
    print(f"\n用户输入: {user_input}")
    
    # 1. 危机评估：由专门的 Agent 判断
    crisis_check_prompt = BaseMessage.make_user_message(
        role_name="用户",
        content=f"请判断以下用户消息是否包含自伤、自杀或严重伤害他人的风险信号：{user_input}"
    )
    
    crisis_response = crisis_evaluator_agent.step(crisis_check_prompt)
    is_crisis = crisis_response.msg.content.strip().lower()

    # 记录危机检测结果到数据库
    save_conversation_message(TEST_USER_ID, "crisis_check", is_crisis)

    # 2. 根据判断结果分流
    if is_crisis == "是":
        print("危机检测结果: 是，进入紧急处理流程。")
        crisis_prompt = BaseMessage.make_user_message(
            role_name="用户",
            content=f"用户表达了严重的危机情绪：{user_input}"
        )
        final_response = crisis_handler_agent.step(crisis_prompt)
        response_content = final_response.msg.content
    else:
        print("危机检测结果: 否，进入正常对话流程。")
        # 正常对话和工具调用
        history = get_user_conversation_history(TEST_USER_ID)
        combined_prompt = BaseMessage.make_user_message(
            role_name="用户",
            content=f"以下是之前的对话历史：\n{history}\n用户当前说：{user_input}"
        )
        
        response = main_agent.step(combined_prompt)
        response_content = response.msg.content
        print("RESPOMSE_INFO")
        print(response.info)
        # 检查是否有工具调用并处理
        if response.info and 'tool_calls' in response.info:
            tool_executed_message = ""
            for tool_call in response.info['tool_calls']:
                tool_name = tool_call.tool_name
                args = tool_call.args
                print(f"Agent 意图调用工具: {tool_name}, 参数: {args}")

                # 修改点：从 FunctionTool 对象的 .func 属性调用
                if tool_name == EmotionRecorderTool.func.__name__:
                    tool_output_json = EmotionRecorderTool.func(**args)
                elif tool_name == ResourceFinderTool.func.__name__:
                    tool_output_json = ResourceFinderTool.func(**args)
                else:
                    tool_output_json = json.dumps({"status": "error", "message": "未知工具"})

                tool_output = json.loads(tool_output_json)
                tool_executed_message += f"\n\n(工具执行结果: {tool_output['message'] if 'message' in tool_output else tool_output_json})"
            
            response_content += tool_executed_message

    # 保存对话并打印最终回复
    save_conversation_message(TEST_USER_ID, "user", user_input)
    save_conversation_message(TEST_USER_ID, "agent", response_content)
    print(f"心理健康助手: {response_content}")

if __name__ == "__main__":
    main_agent, crisis_evaluator_agent, crisis_handler_agent = setup_agent_system()
    
    print("\n--- 心理健康助手系统启动 ---")
    print("你可以输入你的感受。尝试输入'我真的太绝望了，不想活了。'来测试危机干预。")
    print("输入 '退出' 结束对话。")
    
    while True:
        user_input = input("\n> 你: ")
        if user_input.lower() == '退出':
            print("再见！祝你一切顺利。")
            break
        
        run_multi_agent_flow(user_input, main_agent, crisis_evaluator_agent, crisis_handler_agent)