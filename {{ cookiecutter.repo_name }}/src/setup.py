#! /usr/bin/emv python
# -*- coding: utf-8 -*-
"""Install script for {{ cookiecutter.repo_name }}."""

from setuptools import find_packages, setup
import toml

def get_long_description():
    with open("README.md", "r") as readme:
        return readme.read()

# package metadata is loaded from pyproject.toml
# See: [PEP 621 -- Storing project metadata in pyproject.toml] 
# (https://www.python.org/dev/peps/pep-0621)
pyproject_toml = toml.load("pyproject.toml")

if __name__ == "__main__":
    pyproject = pyproject_toml["project"]
    setup(
        name=pyproject["name"],
        long_description=get_long_description(),
        packages=find_packages(where='src/', exclude=["tests", "tests.*"]),
        version=pyproject["version"],
        author=pyproject.get("authors",[{}])[0].get("name"),
        author_email=pyproject.get("authors",[{}])[0].get("email"),
        maintainer=pyproject.get("maintainers",[{}])[0].get("name"),
        maintainer_email=pyproject.get("maintainers",[{}])[0].get("email"),
        requires=pyproject_toml.get("build-system",{}).get("requires"),
        install_requires=pyproject.get("dependencies"),
        extras_require=pyproject.get("optional_dependencies"),
        url=pyproject.get("urls", {}).get("docs"),
        python_requires=pyproject.get("requires-python"),
        # include_package_data=True,
        # package_data={},
    )
