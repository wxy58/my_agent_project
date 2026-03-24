"""  
    总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from rag.vector_store import VectorStoreService
from utils.prompt_load import load_rag_prompt
from model.factory import chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


def print_prompt(prompt):
    print("*"*20)
    print(prompt.to_string())
    print("*"*20)
    return prompt

class RagSummarizeService:
    
    def __init__(self):
        #初始化向量数据库服务
        self.vector_store = VectorStoreService()
        #检索器
        self.retriever = self.vector_store.get_retriever()
        #加载rag提示词文本
        self.prompt_text = load_rag_prompt()
        #初始化提示词模版
        self.prompt_template = PromptTemplate.from_template(
            self.prompt_text
        )
        #初始化模型
        self.model = chat_model
        #初始化链
        self.chain = self.init_chain()
        
    def init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain
    
    def retrieve_docs(self,question:str) -> list[Document]:
        """检索器"""
        # 调用向量数据库的检索器
        # 返回检索到的文档列表
        
        return self.retriever.invoke(question)
    
    def summarize(self,question:str) -> str:
        """总结器"""
        # 调用检索器，获取参考资料
        references = self.retrieve_docs(question)
        context = ""
        counter = 0
        for doc in references:
            counter += 1
            context += f"参考资料{counter}:参考内容{doc.page_content}，参考元数据{doc.metadata}" + "\n"
        # 返回模型的回复
        return self.chain.invoke({
            "input":question,
            "context":context,
        })
        
if __name__ == "__main__":
    rag_service = RagSummarizeService()
    question = "小户型适合哪些扫地机器人"
    print(rag_service.summarize(question))
