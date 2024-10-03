from setuptools import setup, find_packages

setup(
    name="dict2str",
    version="0.0.3",
    keywords=["dict", "markdown", "html", "txt"],
    description="A tool supports converting dictionary to markdown, html and txt.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT Licence",
    url="https://github.com/arcturus-script/dict2str",
    author="ARCTURUS",
    author_email="ice99125@qq.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],
)
