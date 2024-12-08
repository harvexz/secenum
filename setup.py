from setuptools import setup, find_packages

setup(
    name="secenum",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0.1",
        "packaging>=23.0",
        "psutil>=5.9.0",
        "SQLAlchemy>=2.0.0",
        "aiohttp>=3.9.0",
        "python-jose>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "secenum=secenum.interfaces.cli:main",
        ],
    },
    author="Harvey",
    author_email="no-contact@no-email.com",
    description="Advanced System Software Enumeration & Security Assessment Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/harvexz/secenum",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
)