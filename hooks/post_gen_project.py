import os
import shutil
import subprocess

PYPROJECT_FILE = "pyproject.toml"
FALLBACK_PYPROJECT_FILE = "pyproject.toml.fallback"
FALLBACK_SRC = "fallback_src"

# Hooks scripts written in Python will be rendered by Jinja before execution
# `use_rye = {{cookiecutter.use_rye}}` is more reasonable but does not conform to python syntax
use_pre_commit = "{{cookiecutter.use_pre_commit}}" == "True"
use_rye = "{{cookiecutter.use_rye}}" == "True"


def initial_works():
    """
    1. git
    2. basic directory structure
    """
    if use_rye:
        modify_rye_files()
    else:
        fallback_init()


def modify_rye_files():
    """
    by rye:
    1. git
    2. rye style directory structure
    """
    subprocess.check_call(["rye", "sync"])
    subprocess.check_call(["rye", "add", "--dev", "ruff"])

    # Add common configuration written in pyproject.toml.example
    with open(PYPROJECT_FILE, "a") as generated_by_rye, open(FALLBACK_PYPROJECT_FILE) as example:
        generated_by_rye.write("\n" + example.read())

    # Remove fallback files
    os.remove(FALLBACK_PYPROJECT_FILE)
    shutil.rmtree(FALLBACK_SRC)


def fallback_init():
    """
    1. basic directory structure
    2. git
    """
    os.rename(FALLBACK_SRC, "src")
    os.rename(FALLBACK_PYPROJECT_FILE, PYPROJECT_FILE)
    subprocess.check_call(["git", "init"])


def precommit_works():
    """
    requires: git

    1. update pre-commit tool version
    2. pre-commit install
    """
    if not use_pre_commit:
        return

    subprocess.check_call(["pre-commit", "autoupdate"])
    subprocess.check_call(["pre-commit", "install"])


def first_commit():
    """
    requires: git, directory structure, [pre-commit]

    1. git commit
    """
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "first commit"])


if __name__ == "__main__":
    initial_works()
    precommit_works()
    first_commit()
