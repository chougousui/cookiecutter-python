import subprocess

# Hook 脚本用 Python 编写，在执行前会被 Jinja 渲染
# `use_rye = {{cookiecutter.use_rye}}` 更合理但不符合 Python 语法
use_rye = "{{cookiecutter.use_rye}}" == "True"


def init_by_rye():
    """使用 rye 初始化项目"""
    if not use_rye:
        return

    subprocess.check_call(["pwd"])
    subprocess.check_call(["rye", "init"])


def init_by_uv():
    """使用 uv 初始化项目"""
    if use_rye:
        return

    subprocess.check_call(["pwd"])
    # 在当前目录（项目目录）中初始化，不指定目录名以避免创建子文件夹
    subprocess.check_call(["uv", "init", "--python", "3.13", "."])


if __name__ == "__main__":
    init_by_rye()
    init_by_uv()
