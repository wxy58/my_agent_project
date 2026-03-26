import streamlit as st
from agent.react_agent import ReactAgent
import time

#标题
st.title("智扫通智能机器人客服")
st.divider()
#初始化智能体，保存状态
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()
#保存对话记录
if "message" not in st.session_state:
    st.session_state["message"] = []
    
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
    
#用户输入
user_input = st.chat_input(placeholder="请输入您的问题或需求")

if user_input:
    st.chat_message("user").write(user_input)
    #保存用户输入
    st.session_state["message"].append({"role":"user","content":user_input})
    #保存智能体回复
    store_list = []
    with st.spinner("智能客服思考中..."):
        #调用智能体
        res = st.session_state["agent"].execeute_stream(user_input)
        
        def capture_response(chunk,cach_list:list):
            for rs in chunk:
                cach_list.append(rs)
                for char in rs:
                    time.sleep(0.01)
                    yield char
                
        st.chat_message("assistant").write_stream(capture_response(res,store_list))
        st.session_state["message"].append({"role":"assistant","content":store_list[-1]})
        
        #刷新
        st.rerun()
