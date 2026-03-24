"""  
    文件处理
"""
import os,hashlib
from utils.log_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

#获取文件的md5值
def get_file_md5_hex(file_path:str):
    #检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"md5计算错误，文件不存在：{file_path}")
        return None
    #判断是否为文件
    if not os.path.isfile(file_path):
        logger.error(f"md5计算错误，传入的不是文件：{file_path}")
        return None
    
    #计算md5值
    md5_obj = hashlib.md5()
    
    chunk_size = 4096 #4KB分片，避免内存溢出
    try:
        with open(file_path,"rb") as f: #分片必须二进制读取文件
            chunk = f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk)
                chunk = f.read(chunk_size)
                
            #返回md5值
            return md5_obj.hexdigest()
    
    except Exception as e:
        logger.error(f"md5文件{file_path}计算错误，{str(e)}")
        return None

#返回文件夹内的文件列表(允许的文件后缀)
def listdir_with_allowed_type(path:str,allowed_types:tuple[str]):
    
    #检查传入的是不是一个文件夹
    if not os.path.isdir(path):
        logger.error(f"listdir_with_allowed_type错误，传入的不是文件夹：{path}")
        return allowed_types
    
    file_list = []
    
    #写入列表
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            file_list.append(os.path.join(path,f))
    
    return tuple(file_list)#返回的元组不可以修改
def pdf_loader(file_path:str,password=None) -> list[Document]:
    return PyPDFLoader(file_path,password=password).load()

def txt_loader(file_path:str) -> list[Document]:
    return TextLoader(file_path,encoding="utf-8").load()
