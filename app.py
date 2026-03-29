import streamlit as st
from agent.react_agent import ReactAgent
import time
from utils.config_handler import chroma_config
from rag.vector_store import VectorStoreService
import os
from utils.path_tool import get_abs_path

#标题
st.title("🤖 智扫通智能机器人客服")
st.divider()
#初始化智能体，保存状态
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()
#保存对话记录
if "message" not in st.session_state:
    st.session_state["message"] = []
    
if "add_file_service" not in st.session_state:
    st.session_state["add_file_service"] = VectorStoreService()
    
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
    
# #添加文件上传按钮
# up_load_file = st.file_uploader(
#     "上传文件",
#     type = chroma_config["allow_knowledge_file_type"],
#     accept_multiple_files=False
# )
#输入按钮和上传按钮UI合并
up_load_file = None

#初始化上传区域展开状态
if "upload_expanded" not in st.session_state:
    st.session_state["upload_expanded"] = False

col1, col2 = st.columns([10, 1])
with col1:
    st.empty()  #占位符，用于对齐
with col2:
    show_upload = st.button("+", key="upload_toggle")
    
#用户输入
user_input = st.chat_input(placeholder="请输入您的问题或需求")

#处理上传按钮点击
if show_upload:
    st.session_state["upload_expanded"] = not st.session_state["upload_expanded"]
    st.rerun()
    
#根据状态显示或隐藏上传区域
if st.session_state["upload_expanded"]:
    with st.expander("上传文件", expanded=True):
        up_load_file = st.file_uploader(
            "上传文件",
            type = chroma_config["allow_knowledge_file_type"],
            accept_multiple_files=False
        )
    
    
if up_load_file is not None:
    file_name = up_load_file.name
    file_type = up_load_file.type
    file_size = up_load_file.size / 1024
    st.subheader(f"您上传的文件是: {file_name}")#二级标题
    #st.write 小字显示
    st.write(f"文件类型: {file_type}")#文件类型
    st.write(f"文件大小: {file_size:.2f} KB")#文件大小
    #保存上传文件至data目录
    save_dir = get_abs_path(chroma_config["data_path"])
    os.makedirs(save_dir,exist_ok=True)
    with open(os.path.join(save_dir,file_name),"wb") as f:
        f.write(up_load_file.read())
        
    st.success(f"文件{file_name}已保存至{save_dir}")
    
    #加载文件内容到向量数据库
    st.session_state["add_file_service"].load_document()
    st.success(f"文件{file_name}内容已加载到知识库中")
    

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
