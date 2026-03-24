import yaml
from utils.path_tool import get_abs_path

#加载rag配置文件
def load_rag_config(config_path:str = get_abs_path("config/rag.yaml"),encoding:str = "utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
#加载向量数据库配置文件
def load_chroma_config(config_path:str = get_abs_path("config/chroma.yaml"),encoding:str = "utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
#加载prompt配置文件
def load_prompt_config(config_path:str = get_abs_path("config/prompt.yaml"),encoding:str = "utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)

#加载agent配置文件
def load_agent_config(config_path:str = get_abs_path("config/agent.yaml"),encoding:str = "utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    

#创建实例
rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompt_config = load_prompt_config()
agent_config = load_agent_config()


if __name__ == "__main__":
    print(rag_config["chat_model_name"])
