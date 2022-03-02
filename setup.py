from setuptools import setup

with open("README.md", "r") as fh:
    long_description : str = fh.read()

setup(
    name='loggrep',
    version='0.0.1',
    description='grep an ElasticSearch database',
    py_modules=["loggrep"],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.6"
        "Programming Language :: Python :: 3.7",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Logging",
        "Typing :: Typed",
        "Operating System :: OS Independent"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = [
        "elasticsearch7"
    ],
    extras_require = {
        "dev": [
            "pytest>=3.7",
            "twine"
        ]
    }
)
