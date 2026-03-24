"""  
    为整个工程提供统一的绝对路径
"""
import os


def get_project_root() -> str:
    """ 
        获取工程所在的根目录路径
    """
    # 获取当前文件的绝对路径
    current_file = os.path.abspath(__file__)
    #获取文件所在的文件夹路径
    current_dir = os.path.dirname(current_file)
    #获取文件夹所在的文件夹路径，即工程根目录
    project_root = os.path.dirname(current_dir)
    
    return project_root

def get_abs_path(relative_path: str) -> str:
    """ 
        传递相对路径，返回绝对路径
    """
    # 获取工程根目录路径
    project_root = get_project_root()
    #获取相对路径的绝对路径，形成一个完整的绝对路径
    abs_path = os.path.join(project_root,relative_path)
    return abs_path

if __name__ == "__main__":
    print(get_abs_path("config/config.json"))
