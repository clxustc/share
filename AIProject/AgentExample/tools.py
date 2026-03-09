import os
from typing import List, Optional, Union, TextIO


def read_file(file_path: str, encoding: str = "utf-8", mode: str = "r") -> Union[str, bytes]:
    """
    读取文件内容，支持文本模式和二进制模式。

    该函数提供了安全的文件读取方式，自动处理文件打开/关闭，
    并捕获常见的文件读取异常（如文件不存在、权限不足等）。

    Parameters:
        file_path: str
            要读取的文件的完整路径或相对路径（必填）
        encoding: str, optional
            文本模式下的文件编码格式，默认值为"utf-8"
        mode: str, optional
            文件打开模式，支持"r"（文本读取，默认）、"rb"（二进制读取）

    Returns:
        Union[str, bytes]:
            - 文本模式（"r"）返回字符串类型的文件内容
            - 二进制模式（"rb"）返回bytes类型的文件内容

    Raises:
        ValueError: 传入不支持的打开模式时触发
        FileNotFoundError: 文件路径不存在时触发
        PermissionError: 无文件读取权限时触发
        IOError: 其他文件读取相关错误时触发

    Examples:
        >>> # 读取文本文件
        >>> content = read_file("example.txt", encoding="utf-8")
        >>> print(content[:100])  # 打印前100个字符

        >>> # 读取二进制文件（如图片、视频）
        >>> bin_content = read_file("image.png", mode="rb")
        >>> print(len(bin_content))  # 打印文件字节数
    """
    # 验证模式合法性
    if mode not in ("r", "rb"):
        raise ValueError(f"不支持的打开模式：{mode}，仅支持'r'或'rb'")
    
    try:
        with open(file_path, mode=mode, encoding=encoding if mode == "r" else None) as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在：{file_path}")
    except PermissionError:
        raise PermissionError(f"无读取权限：{file_path}")
    except Exception as e:
        raise IOError(f"读取文件失败：{file_path}，错误信息：{str(e)}")


def list_files(dir_path: str, extension: Optional[str] = None, include_subdirs: bool = False) -> List[str]:
    """
    列出指定目录下的文件路径，支持按文件扩展名筛选和递归子目录。

    该函数仅返回文件（不包含目录），返回的路径为绝对路径，便于后续文件操作。

    Parameters:
        dir_path: str
            要遍历的目录路径（必填）
        extension: Optional[str], optional
            筛选的文件扩展名（如".txt"、".csv"），None表示不筛选（默认）
            注意：扩展名需包含前缀点，区分大小写（如".TXT"和".txt"视为不同）
        include_subdirs: bool, optional
            是否递归遍历子目录，默认值为False（仅遍历当前目录）

    Returns:
        List[str]:
            符合条件的文件绝对路径列表，列表为空表示无匹配文件

    Raises:
        NotADirectoryError: 传入的路径不是有效目录时触发
        PermissionError: 无目录访问权限时触发
        OSError: 其他目录遍历相关错误时触发

    Examples:
        >>> # 列出当前目录下所有txt文件
        >>> txt_files = list_files("./", extension=".txt")
        >>> print(f"找到{len(txt_files)}个txt文件")

        >>> # 递归列出指定目录下所有csv文件
        >>> csv_files = list_files("/data", extension=".csv", include_subdirs=True)
        >>> for file in csv_files[:5]:
        ...     print(file)
    """
    # 验证目录合法性
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"不是有效目录：{dir_path}")
    
    matched_files = []
    abs_dir = os.path.abspath(dir_path)
    
    try:
        # 遍历目录（递归/非递归）
        walk_generator = os.walk(abs_dir) if include_subdirs else [(abs_dir, [], os.listdir(abs_dir))]
        
        for root, _, files in walk_generator:
            for file_name in files:
                # 按扩展名筛选
                if extension is not None:
                    if not file_name.endswith(extension):
                        continue
                # 拼接绝对路径并添加到结果
                file_path = os.path.join(root, file_name)
                matched_files.append(file_path)
        
        return matched_files
    except PermissionError:
        raise PermissionError(f"无访问权限：{abs_dir}")
    except Exception as e:
        raise OSError(f"遍历目录失败：{abs_dir}，错误信息：{str(e)}")


def rename_file(old_file_path: str, new_file_path: str, overwrite: bool = False) -> bool:
    """
    重命名文件（支持跨目录移动），可配置是否覆盖已存在的目标文件。

    该函数会先验证源文件存在性，再执行重命名操作，避免误操作。

    Parameters:
        old_file_path: str
            原文件的完整路径或相对路径（必填）
        new_file_path: str
            新文件的完整路径或相对路径（必填）
        overwrite: bool, optional
            若目标文件已存在，是否覆盖，默认值为False（不覆盖，触发异常）

    Returns:
        bool:
            重命名成功返回True，无其他返回值

    Raises:
        FileNotFoundError: 原文件不存在时触发
        FileExistsError: 目标文件已存在且overwrite=False时触发
        PermissionError: 无文件重命名/覆盖权限时触发
        OSError: 其他文件重命名相关错误时触发

    Examples:
        >>> # 简单重命名（同目录）
        >>> rename_file("old_name.txt", "new_name.txt")

        >>> # 重命名并移动到其他目录（覆盖已存在文件）
        >>> rename_file(
        ...     old_file_path="./data/old.csv",
        ...     new_file_path="./backup/new.csv",
        ...     overwrite=True
        ... )
    """
    # 验证源文件存在性
    if not os.path.isfile(old_file_path):
        raise FileNotFoundError(f"原文件不存在：{old_file_path}")
    
    # 处理目标文件已存在的情况
    if os.path.exists(new_file_path):
        if not overwrite:
            raise FileExistsError(f"目标文件已存在：{new_file_path}，请设置overwrite=True覆盖")
        # 若覆盖，先删除目标文件（避免os.rename在Windows下的权限问题）
        try:
            os.remove(new_file_path)
        except Exception as e:
            raise OSError(f"删除已存在的目标文件失败：{new_file_path}，错误信息：{str(e)}")
    
    try:
        # 执行重命名（支持跨目录移动）
        os.rename(old_file_path, new_file_path)
        return True
    except PermissionError:
        raise PermissionError(f"无权限重命名文件：{old_file_path} → {new_file_path}")
    except Exception as e:
        raise OSError(f"重命名文件失败：{old_file_path} → {new_file_path}，错误信息：{str(e)}")


# 测试示例（可选，取消注释可运行）
if __name__ == "__main__":
    pass
    # 1. 测试list_files
    # files = list_files("./", extension=".py")
    # print(f"当前目录下的py文件：{files}")

    # 2. 测试read_file
    # try:
    #     content = read_file("test.txt", encoding="utf-8")
    #     print(f"文件内容：{content[:50]}")
    # except Exception as e:
    #     print(f"读取失败：{e}")

    # 3. 测试rename_file
    # try:
    #     # 先创建测试文件
    #     with open("test_rename_old.txt", "w") as f:
    #         f.write("test")
    #     rename_file("test_rename_old.txt", "test_rename_new.txt")
    #     print("重命名成功")
    # except Exception as e:
    #     print(f"重命名失败：{e}")
