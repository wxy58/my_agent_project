from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
import os
from utils.config_handler import agent_config
from  utils.path_tool import get_abs_path
from utils.log_handler import logger


rag = RagSummarizeService()
user_id = ["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010"]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

#生成外部数据
"""    
    形式：
    {
        "user_id":{
            "month":{"key":value}
            ...
        }
        ...
    }
"""
#定义存储全局变量
external_data = {}

def generate_external_data():
    
    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query:str) -> str:
    """总结器"""
    return rag.summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city:str) -> str:
    return f"城市{city}的天气是晴朗，温度25摄氏度，湿度60%。，南风1级，AQI21，最近六小时无雨"

@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_city() -> str:
    return random.choice(["北京","上海","广州","深圳"])

@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_id)

@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() ->str:
    return random.choice(month_arr)

@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回，如果未检索到则返回空字符串")
def fetch_external_data(user_id:str, month:str) -> str:
    generate_external_data()
    
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"fetch_external_data: {user_id} {month} 未检索到使用记录")
        return ""

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，作用为为后续提示词切换提供上下文信息。")
def fill_context_for_report():
    """工具的作用为满足提示词中的工具栏，为提示词切换提供切换标记。"""
    return "fill_context_for_report已调用"