from langchain.agents.middleware import wrap_tool_call, ToolCallRequest, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from utils.log_handler import logger
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from utils.prompt_load import load_system_prompt, load_report_prompt


@wrap_tool_call
def monitor_tool(
    #请求调用工具时的输入数据封装
    request:ToolCallRequest,
    #调用的工具函数
    handle:callable[[ToolCallRequest],ToolMessage | Command],
) -> ToolMessage | Command:
    """"工具执行的监控"""
    #将执行过程记录到日志中
    logger.info(f"[monitor_tool]执行工具：{request.tool_call['name']}")
    logger.info(f"[monitor_tool]执行工具的传入参数：{request.tool_call['args']}")
    
    try:
        #打印工具执行过程中的信息以及结果
        result = handle(request)
        logger.info(f"[monitor_tool]工具{request.tool_call['name']}执行成功，返回结果：{result}")
        #结合工具链，检测是否调用fill_context_for_report工具
        if request.tool_call["name"] == "fill_context_for_report":
            request.runtime.context["report"] = True    #默认false，为提示词切换提供切换标记
        
        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}执行失败，错误信息：{str(e)}")
        raise e
    
@before_model
def log_before_model(
    state:AgentState,   #整个Agent智能体中的状态记录
    runtime:Runtime,    #当前运行时环境的上下文信息
):
    """在模型执行前输出日志"""
    logger.info(f"[log_before_model]即将调用的模型，带有{len(state['messages'])}条消息")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__}, {state['messages'][-1].content.strip()}") 
    
    return None

@dynamic_prompt
#每一次在生成提示词之前，调用此函数
def report_prompt_switch(request:ModelRequest):
    """动态切换提示词"""
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompt()
    
    return load_system_prompt()