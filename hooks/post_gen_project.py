import logging
import os
import shutil
import subprocess

import requests
import yaml

# 配置日志
logging.basicConfig(level=logging.INFO)

PYPROJECT_FILE = "pyproject.toml"
TEMPLATE_PYPROJECT_FILE = "pyproject.toml.template"
FALLBACK_SRC = "fallback_src"

# Hook 脚本用 Python 编写，在执行前会被 Jinja 渲染
# `use_rye = {{cookiecutter.use_rye}}` 更合理但不符合 Python 语法
use_pre_commit = "{{cookiecutter.use_pre_commit}}" == "True"
use_rye = "{{cookiecutter.use_rye}}" == "True"


def initial_works():
    """
    初始化工作:
    1. git
    2. 基础目录结构
    """
    if use_rye:
        modify_rye_files()
    else:
        uv_post_process()


def modify_rye_files():
    """
    使用 rye 的后处理:
    1. git
    2. rye 风格的目录结构
    """
    subprocess.check_call(["rye", "sync"])
    subprocess.check_call(["rye", "add", "--dev", "ruff", "pyright", "typos"])

    # 添加 pyproject.toml.template 中的通用配置
    with open(PYPROJECT_FILE, "a") as generated_by_rye, open(TEMPLATE_PYPROJECT_FILE) as template:
        generated_by_rye.write("\n" + template.read())

    # 移除模板文件
    os.remove(TEMPLATE_PYPROJECT_FILE)
    if os.path.exists(FALLBACK_SRC):
        shutil.rmtree(FALLBACK_SRC)


def uv_post_process():
    """
    使用 uv 的后处理:
    1. 移动 main.py 到 src/main.py
    2. 添加开发依赖
    3. 追加工具配置到 pyproject.toml
    4. 初始化 git（uv init 已在 pre hook 中完成项目初始化）
    """
    # 移动 main.py 到 src/main.py (uv init 在根目录创建 main.py)
    if os.path.exists("main.py"):
        os.makedirs("src", exist_ok=True)
        shutil.move("main.py", "src/main.py")

    # 添加开发依赖
    subprocess.check_call(["uv", "add", "--dev", "ruff", "pyright", "typos"])

    # 添加 pyproject.toml.template 中的通用配置
    with open(PYPROJECT_FILE, "a") as generated_by_uv, open(TEMPLATE_PYPROJECT_FILE) as template:
        generated_by_uv.write("\n" + template.read())

    # 移除模板文件
    os.remove(TEMPLATE_PYPROJECT_FILE)
    if os.path.exists(FALLBACK_SRC):
        shutil.rmtree(FALLBACK_SRC)

    # 初始化 git（如果 uv init 没有初始化的话）
    if not os.path.exists(".git"):
        subprocess.check_call(["git", "init"])


def precommit_works():
    """
    pre-commit 相关工作:
    需要: git

    1. 更新 pre-commit 工具版本
    2. 修复工具版本问题
    3. 安装 pre-commit 钩子
    """
    if not use_pre_commit:
        return

    subprocess.check_call(["pre-commit", "autoupdate"])
    _fix_typos_rev()
    subprocess.check_call(["pre-commit", "install"])
    subprocess.check_call(["pre-commit", "install", "--hook-type", "commit-msg"])


def first_commit():
    """
    首次提交:
    需要: git, 目录结构, [pre-commit]

    1. git add
    2. 运行 pre-commit 修复格式问题
    3. 重新 git add 修复后的文件
    4. git commit
    """
    subprocess.check_call(["git", "add", "."])

    # 如果启用了 pre-commit，先运行一次来修复格式问题
    if use_pre_commit:
        try:
            logging.info("Running pre-commit to fix formatting issues...")
            subprocess.check_call(["pre-commit", "run", "--all-files"])
            logging.info("Pre-commit fixes applied, re-adding files...")
            # 重新添加被 pre-commit 修复的文件
            subprocess.check_call(["git", "add", "."])
        except subprocess.CalledProcessError:
            # pre-commit 可能会返回非零状态码（即使修复了问题）
            # 所以我们忽略错误并重新 add 文件
            logging.info("Pre-commit made changes, re-adding files...")
            subprocess.check_call(["git", "add", "."])

    subprocess.check_call(["git", "commit", "-m", "chore: first commit"])


def _fix_typos_rev():
    """
    pre-commit autoupdate时，由于pre-commit自己的逻辑问题，
    会错误地将typos的rev更新为"v1"
    这里手动修复这个问题
    """
    config_file = ".pre-commit-config.yaml"
    if not os.path.exists(config_file):
        logging.warning(f"{config_file} not found, skipping typos fix")
        return

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        for repo in config.get("repos", []):
            if repo.get("repo") == "https://github.com/crate-ci/typos" and repo.get("rev") == "v1":
                logging.info("Found typos repo with rev 'v1', fixing...")
                new_rev = _get_latest_typos_rev()
                repo["rev"] = new_rev
                logging.info(f"Updated typos rev from 'v1' to '{new_rev}'")
                break

        with open(config_file, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)
    except Exception as e:
        logging.warning(f"Failed to fix typos rev: {e}")


def _get_latest_typos_rev():
    """
    获取typos的最新rev
    如果获取失败则返回固定版本v1.34.0
    """
    url = "https://api.github.com/repos/crate-ci/typos/releases/latest"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()["tag_name"]
    except Exception as e:
        logging.warning(f"Failed to fetch latest typos version: {e}")
        return "v1.34.0"


if __name__ == "__main__":
    initial_works()
    precommit_works()
    first_commit()
