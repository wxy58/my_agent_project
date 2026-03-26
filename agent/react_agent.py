from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_load import load_system_prompt
from agent.tools.agent_tools import *
from agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch

#创建智能体
class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt=load_system_prompt(),
            tools = [rag_summarize,get_weather,get_user_city,get_user_id,get_current_month,fetch_external_data,fill_context_for_report],
            middleware=[monitor_tool,log_before_model,report_prompt_switch],
        )
        
    def execeute_stream(self,question:str):
        #输入的消息
        input_dict = {
            "messages":[
                {"role":"user","content":question}
            ]
        }
        
        #返回结果
        #context的report参数为自定义新增参数，用于切换提示词模版的标志
        res = self.agent.stream(input_dict,stream_mode="values",context={"report":False})
        for chunk in res:
            last_message = chunk["messages"][-1]
            if last_message.content:
                #yield逐一的返回结果，返回一个生成器(迭代器)对象
                yield last_message.content.strip() + "\n"
       
if __name__ == "__main__":
    react_agent = ReactAgent()
    for chunk in react_agent.execeute_stream("给我生成我的使用报告"):
        print(chunk, end="",flush=True)
