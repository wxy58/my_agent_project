from langchain_chroma import Chroma
from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from model.factory import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.log_handler import logger
from utils.file_handler import get_file_md5_hex,listdir_with_allowed_type,pdf_loader,txt_loader
from langchain_core.documents import Document

"""   
    作用：提供向量数据库的服务，包括加载文档、检索文档等操作
"""
class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name = chroma_config["collection_name"],
            embedding_function= embedding_model,
            persist_directory = get_abs_path(chroma_config["persist_directory"]),
        )
        #文本分割器
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function=len,
        )
    #获取检索器
    def get_retriever(self):
        return self.vector_store.as_retriever(
            search_kwargs = {"k": chroma_config["k"]}
        )
        
    def load_document(self):
        """  
            从数据文件夹内读取数据文件，进行检查，没有变更则不加载，有变更则转为向量存入向量数据库
        """
        
        def check_md5(md5_for_check:str):
            """  
                检查文件是否变更，没有则Flase
                如果文件不存在，返回None
            """
            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
                #创建文件
                open(get_abs_path(chroma_config["md5_hex_store"]), "w", encoding="utf-8").close()
                return False    #文件没变更
            
            #读取文件内容
            with open(get_abs_path(chroma_config["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True    #文件已经存在知识库中
                    
                return False    #文件未存在知识库中。
            
        def save_md5(md5_for_check:str):
            """  
                保存文件的MD5值到文件
            """
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")
                
        def get_file_documents(read_path:str ):
            """ 
                获取文件的list[Document]对象
            """
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            elif read_path.endswith(".txt"):
                return txt_loader(read_path)
            else:
                logger.error(f"get_file_documents错误，传入的不是pdf或txt文件：{read_path}")
                return None
            
        allowed_file_path:list[str] = listdir_with_allowed_type(get_abs_path(chroma_config["data_path"]),tuple(chroma_config["allow_knowledge_file_type"]))
        
        for file in allowed_file_path:
            #获取文件md5值
            md5 = get_file_md5_hex(file)
            #检查文件是否存在向量知识库中
            if check_md5(md5):
                logger.info(f"文件{file}内容已存在知识库中，跳过")
                continue
            #不存在则将文件内容存入向量数据库
            try:
                documents:list[Document] = get_file_documents(file)
                if not documents:
                    logger.warning(f"文件{file}内没有有效文本内容，跳过")
                    continue
                
                splited_documents = self.spliter.split_documents(documents)
                if not splited_documents:
                    logger.warning(f"分片后，文件{file}内没有有效文本内容，跳过")
                    continue
                
                #将分片后的文档存入向量数据库
                self.vector_store.add_documents(splited_documents)
                #保存文件的MD5值
                save_md5(md5)
                logger.info(f"文件{file}内容已加载到知识库中")
                
            except Exception as e:
                #exc_info=True 记录详细的错误信息，为flase则不记录详细信息
                logger.error(f"加载文件{file}内容到知识库中出错：{str(e)}",exc_info=True)
                continue
            
            
if __name__ == "__main__":
    vs = VectorStoreService()
    vs.load_document()
    
    retriever = vs.get_retriever()
    
    res = retriever.invoke("迷路")
    for i in res:
        print(i.page_content)
        print("="*20)
                
                
                   
        
        
   