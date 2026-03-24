"""  
    提供不同的模型,
"""
from abc import ABC, abstractmethod
from typing import Optional
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from utils.config_handler import rag_config

#抽象类abc
class BaseModelFactory(ABC):
    #抽象方法
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass
    
#具体实现
class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_config["chat_model_name"])
    
#具体实现
class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_config["embedding_model_name"])
    
#创建实例
chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingsFactory().generator()
