from utils.config_handler import prompt_config
from utils.path_tool import get_abs_path
from utils.log_handler import logger

def load_system_prompt():
    try:
        system_prompt_path = get_abs_path(prompt_config["main_prompt_path"])
    
    except KeyError as e:
        logger.error(f"[load_system_prompt] 在yaml配置文件中缺少main_prompt_path键")
        raise e
    
    try:
        return open(system_prompt_path,"r",encoding="utf-8").read()
    
    except Exception as e:
        logger.error(f"[load_system_prompt]解析系统提示词出错，错误信息：{e}")
        raise e
    
def load_rag_prompt():
    try:
        rag_prompt_path = get_abs_path(prompt_config["rag_summarize_prompt_path"])
    
    except KeyError as e:
        logger.error(f"[load_rag_prompt] 在yaml配置文件中缺少rag_summarize_prompt_path键")
        raise e
    
    try:
        return open(rag_prompt_path,"r",encoding="utf-8").read()
    
    except Exception as e:
        logger.error(f"[load_rag_prompt]解析rag提示词出错，错误信息：{e}")
        raise e
    
def load_report_prompt():
    try:
        report_prompt_path = get_abs_path(prompt_config["report_prompt_path"])
    
    except KeyError as e:
        logger.error(f"[load_report_prompt] 在yaml配置文件中缺少report_prompt_path键")
        raise e
    
    try:
        return open(report_prompt_path,"r",encoding="utf-8").read()
    
    except Exception as e:
        logger.error(f"[load_report_prompt]解析报告提示词出错，错误信息：{e}")
        raise e
    
    
if __name__ == "__main__":
    print(load_system_prompt())
    
   
