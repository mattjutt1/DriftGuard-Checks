#!/usr/bin/env python3
"""
PromptEvolver CLI Setup
Simple setup script for the CLI tool
"""

from setuptools import setup, find_packages

setup(
    name="promptevolver-cli",
    version="0.1.0",
    description="CLI tool for PromptEvolver - Terminal-based prompt optimization using Microsoft PromptWizard",
    author="PromptEvolver",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "rich>=12.0.0",  # For better terminal output
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "promptevolver=promptevolver_cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
