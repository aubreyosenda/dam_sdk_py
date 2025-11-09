from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dam-sdk-py",
    version="1.0.0",
    author="Aubrey Osenda",
    author_email="aubrey@example.com",
    description="Official Python SDK for DAM System - Digital Asset Management API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aubreyosenda/dam_sdk_py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "async": ["aiohttp>=3.8.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=0.910",
        ],
        "django": ["Django>=3.2"],
        "flask": ["Flask>=2.0"],
        "fastapi": ["fastapi>=0.68.0"],
    },
    keywords=[
        "dam",
        "digital-asset-management",
        "file-upload",
        "image-processing",
        "api-client",
        "sdk",
        "media-management"
    ],
    project_urls={
        "Documentation": "https://github.com/aubreyosenda/dam_sdk_py/wiki",
        "Source": "https://github.com/aubreyosenda/dam_sdk_py",
        "Tracker": "https://github.com/aubreyosenda/dam_sdk_py/issues",
    },
)