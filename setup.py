"""
ESP32 PLC GUI Setup Script
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="esp32-plc-gui",
    version="1.0.0",
    author="Bradley Daniels",
    author_email="your-email@example.com",  # Update with your email
    description="A professional flowchart-style PLC programming environment for ESP32-S3 microcontrollers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Bradd1389/ESP32_PLC_GUI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "esp32-plc-gui=Main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.json", "*.md", "*.txt"],
    },
    keywords="esp32 plc gui flowchart microcontroller embedded automation",
    project_urls={
        "Bug Reports": "https://github.com/Bradd1389/ESP32_PLC_GUI/issues",
        "Source": "https://github.com/Bradd1389/ESP32_PLC_GUI",
        "Documentation": "https://github.com/Bradd1389/ESP32_PLC_GUI/blob/main/README.md",
    },
)
