from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random

rag = RagSummarizeService()
user_id = ["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010"]

@tool(description="从向量存储中检索参考资料")
def rag_summarize(question:str) -> str:
    """总结器"""
    return rag.summarize(question)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(location:str) -> str:
    return f"城市{location}的天气是晴朗，温度25摄氏度，湿度60%。，南风1级，AQI21，最近六小时无雨"

@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_city() -> str:
    return random.choice(["北京","上海","广州","深圳"])

@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_id)

@tool(description="")
def get_current_month():
    pass