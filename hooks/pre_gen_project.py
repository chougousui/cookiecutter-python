import subprocess

# Hooks scripts written in Python will be rendered by Jinja before execution
# `use_rye = {{cookiecutter.use_rye}}` is more reasonable but does not conform to python syntax
use_rye = "{{cookiecutter.use_rye}}" == "True"


def init_by_rye():
    if not use_rye:
        return

    subprocess.check_call(["pwd"])
    subprocess.check_call(["rye", "init"])


if __name__ == "__main__":
    init_by_rye()
