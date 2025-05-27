from setuptools import setup, find_packages

setup(
    name="data_testing",
    version="0.1",
    packages=find_packages(where="utils"),
    package_dir={"": "utils"},
)
