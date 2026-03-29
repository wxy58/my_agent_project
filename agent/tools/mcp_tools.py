# 导入FastMCP框架，用于快速构建MCP工具服务
from typing import Any,Dict,Optional
from mcp.server.fastmcp import FastMCP
import httpx
from utils.config_handler import agent_config

# 创建一个 MCP 服务器
mcp_server = FastMCP("amap-weather")

# 高德地图API相关全局配置
AMAP_API_BASE = "https://restapi.amap.com/v3"  # 高德地图API的基础请求地址
AMAP_API_KEY = agent_config["AMAP_API_KEY"]  # 高德地图API密钥（必填）

# 申请地址：https://lbs.amap.com/
USER_AGENT = "amap-weather-app/1.0"  # 请求头中的用户代理标识，用于标识请求来源

# ========================================
# 核心工具函数：高德API请求发送
# ========================================
async def make_amap_request(endpoint: str, params: dict) -> Optional[Dict[str, Any]]:
    """
    封装高德地图API的异步请求发送逻辑，包含完整的错误处理机制

    Args:
        endpoint: API接口路径（如"/weather/weatherInfo"，需以/开头）
        params: 接口所需的业务请求参数（无需包含key和output）

    Returns:
        Optional[Dict[str, Any]]: 成功返回API响应的JSON数据字典，失败返回None
    """
    print('正在发送高德API请求...make_amap_request')
    
    # 构造基础请求参数，所有接口都需要携带key和output格式指定
    base_params = {
        'key': AMAP_API_KEY,  # 接口调用凭证，必填
        'output': 'JSON'      # 指定响应数据格式为JSON，方便后续解析
    }
    
    # 合并基础参数和业务参数（业务参数可覆盖基础参数，提升灵活性）
    full_params = {**base_params, **params}

    # 异步创建HTTP客户端，使用上下文管理器自动管理客户端生命周期
    async with httpx.AsyncClient() as client:
        try:
            # 发送GET异步请求，获取高德API响应
            response = await client.get(
                url=f'{AMAP_API_BASE}{endpoint}',  # 拼接完整的请求URL
                params=full_params,                # 传递拼接后的完整请求参数
                headers={'User-Agent': USER_AGENT},# 设置请求头，标识客户端身份
                timeout=30.0                       # 设置30秒请求超时时间，防止长时间阻塞
            )
            
            # 检查HTTP响应状态码，非2xx状态码会抛出HTTPStatusError异常
            response.raise_for_status()
            
            # 解析响应数据为JSON格式（字典类型）
            data = response.json()

            # 处理高德API自身的业务错误（HTTP状态码200不代表业务请求成功）
            # 高德API约定：status为'1'表示业务请求成功，其他值为失败
            if data.get("status") != '1':
                err_msg = data.get("info", "未知错误")  # 获取API返回的错误描述信息
                print(f"高德API请求失败: {err_msg}")
                return None
            
            # 业务请求成功，返回解析后的JSON数据
            return data
        
        # 捕获所有可能的异常（网络异常、超时、JSON解析失败等）
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None

# ========================================
# 数据格式化函数：天气数据转可读文本
# ========================================
def format_weather_forecast(data: Dict[str, Any]) -> str:
    """
    格式化实时天气数据，转换为人类可读的简洁文本

    Args:
        data: 高德API返回的天气数据字典

    Returns:
        str: 格式化后的简洁天气信息字符串
    """
    try:
        # 校验数据是否包含有效实时天气字段（lives为高德API实时天气数据关键字段）
        if 'lives' in data and data['lives']:
            weather_info = data['lives'][0]  # 取第一个元素（对应查询城市的天气数据）
            city = weather_info.get('city', '未知城市')    # 城市名称
            weather = weather_info.get('weather', '未知天气')  # 天气状况
            temperature = weather_info.get('temperature', '未知')  # 温度
            humidity = weather_info.get('humidity', '未知')  # 湿度
            winddirection = weather_info.get('winddirection', '未知')  # 风向
            windpower = weather_info.get('windpower', '未知')  # 风力

            # 拼接简洁的天气信息字符串并返回
            return f"{city}天气：{weather}，温度：{temperature}℃，湿度：{humidity}%，风向：{winddirection}，风力：{windpower}级"
        else:
            # 数据中无有效实时天气字段
            return "未找到天气信息"
    except Exception as e:
        # 捕获数据格式化过程中的异常（如字段缺失、类型错误等）
        print(f"格式化天气数据时出错: {str(e)}")
        return "天气数据格式错误"

# ========================================
# 数据格式化函数：IP定位数据转可读文本
# ========================================
def format_ip_location(data: Dict[str, Any]) -> str:
    """
    格式化IP定位数据，转换为人类可读的地理位置信息

    Args:
        data: 高德API返回的IP定位数据字典

    Returns:
        str: 格式化后的地理位置信息字符串
    """
    try:
        # 校验数据是否包含有效定位字段
        if 'province' in data:
            province = data.get('province', '未知省份')
            city = data.get('city', '未知城市')
            district = data.get('district', '未知区县')
            adcode = data.get('adcode', '')
            rectangle = data.get('rectangle', '')
            
            location_info = f"省份：{province}，城市：{city}，区县：{district}"
            if adcode:
                location_info += f"，行政区划代码：{adcode}"
            if rectangle:
                location_info += f"，经纬度范围：{rectangle}"
            
            print(location_info)
            
            return str(city)
        else:
            return "未找到IP定位信息"
    except Exception as e:
        print(f"格式化IP定位数据时出错: {str(e)}")
        return "IP定位数据格式错误"
    
# ========================================
# MCP工具注册：对外暴露的天气查询接口
# ========================================
@mcp_server.tool()
async def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息

    Args:
        city: 城市名称（如"北京"、"上海"，支持中文全称）

    Returns:
        str: 格式化后的简洁天气信息字符串
    """
    # 构造天气查询请求参数
    params = {
        'city': city,                # 目标城市名称
        'extensions': 'base'         # 查询类型：base=实时天气，all=未来天气预报
    }

    # 调用封装的高德API请求函数，获取天气数据
    data = await make_amap_request("/weather/weatherInfo", params)

    # 校验数据是否获取成功，返回对应结果
    if data is None:
        return "获取天气信息失败，请检查网络连接或API配置"

    # 格式化天气数据并返回
    return format_weather_forecast(data)

# ========================================
# MCP工具注册：对外暴露的IP定位接口
# ========================================
@mcp_server.tool()
async def get_city_by_ip() -> str:
    """
    获取用户当前IP地址所在的城市信息

    Returns:
        str: 格式化后的地理位置信息字符串
    """
    # 调用封装的高德API请求函数，获取IP定位数据
    # 不传ip参数，高德API会自动识别客户端IP
    data = await make_amap_request("/ip", {})

    # 校验数据是否获取成功，返回对应结果
    if data is None:
        return "获取IP定位信息失败，请检查网络连接或API配置"

    # 直接返回整个data字典中的定位信息
    return format_ip_location(data)

async def get_location_weather() -> str:
    """   
        根据用户所在ip地址，返回该城市的天气信息
    """
    ip_city = await get_city_by_ip()
    weather_info = await get_weather(ip_city)
    return weather_info


if __name__ == "__main__":
    import asyncio
    info = asyncio.run(get_location_weather())
    print(info)
    




