# {{cookiecutter.project_name}}

Nothing to see here, just a tumbleweed rolling by.

## 开发环境

{% if cookiecutter.use_rye -%}
这个项目使用 [Rye](https://rye-up.com/) 进行包管理。

### 安装依赖

```bash
rye sync
```

### 添加依赖

```bash
# 添加运行时依赖
rye add requests

# 添加开发依赖
rye add --dev pytest
```

### 运行命令

```bash
# 在项目环境中运行命令
rye run python src/main.py

# 运行测试
rye run pytest
```

### 其他常用命令

```bash
# 查看依赖
rye list

# 更新依赖
rye sync --update-all

# 移除依赖
rye remove requests
```

{% else -%}
这个项目使用 [UV](https://docs.astral.sh/uv/) 进行包管理。

### 安装依赖

```bash
uv sync
```

### 添加依赖

```bash
# 添加运行时依赖
uv add requests

# 添加开发依赖
uv add --dev pytest

# 添加可选依赖组
uv add --optional web fastapi uvicorn
```

### 运行命令

```bash
# 在项目环境中运行命令
uv run python src/main.py

# 运行测试
uv run pytest
```

### 其他常用命令

```bash
# 查看依赖
uv tree

# 更新依赖
uv sync --upgrade

# 移除依赖
uv remove requests

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

{% endif -%}

## 代码格式化和检查

```bash
{% if cookiecutter.use_rye -%}
rye run format:check     # 格式化检查
rye run lint             # 代码检查
rye run typecheck        # 类型检查
rye run typos            # 拼写检查
rye run fixall          # 一键修复所有问题
{% else -%}
# 检查问题
uv run ruff check             # 代码检查
uv run pyright                # 类型检查
uv run typos                  # 拼写检查
uv run ruff format --check    # 格式化检查

# 修复问题
uv run ruff check --fix
uv run typos -w
uv run ruff format
{% endif %}
```

{% if cookiecutter.use_pre_commit -%}
## Pre-commit 钩子

项目配置了 pre-commit 钩子，会在提交时自动运行代码检查。

```bash
# 手动运行所有钩子
pre-commit run --all-files

# 更新钩子版本
pre-commit autoupdate
```
{% endif -%}
