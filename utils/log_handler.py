import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

#日志保存的根目录
LOG_ROOT = get_abs_path("logs")

#确保日志根目录存在
os.makedirs(LOG_ROOT,exist_ok=True)

#日志的格式配置
DEFAULT_LOG_FORMAT = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")    # 日志格式 时间 - 日志名称 - 日志等级 - 文件名:行号 - 日志消息

def get_logger(
    # 日志名称
    name:str = "agent",
    # 控制台日志等级
    console_level:int = logging.INFO,
    #文件日志等级
    file_level:int = logging.DEBUG,
    log_file = None
) ->logging.Logger:
    #创建日志管理器
    logger = logging.getLogger(name)
    #设置日志等级
    logger.setLevel(logging.DEBUG)
    
    #避免重复添加日志处理器
    if logger.handlers:
        return logger
    #创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    #将控制台日志处理器添加到日志管理器
    logger.addHandler(console_handler)
    #日志文件的存放路径
    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    #创建文件日志处理器
    file_handler = logging.FileHandler(log_file,mode="w",encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    #将文件日志处理器添加到日志管理器
    logger.addHandler(file_handler)
    return logger

#快捷获取日志管理器
logger = get_logger()

if __name__ == "__main__":
    logger.info("这是一条info日志")
    logger.debug("这是一条debug日志")
    logger.error("这是一条error日志")
    logger.warning("这是一条warning日志")
    logger.critical("这是一条critical日志")
   