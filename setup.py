from setuptools import setup, find_packages

setup(
    name="qutils",
    version="0.1.0",
    packages=find_packages(),
    description="A Python abstraction layer for qemu-img",
    author="Antigravity",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
