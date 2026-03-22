from setuptools import setup, find_packages

setup(
    name             = "pipeschrod",
    version          = "1.0.0",
    author           = "Dr. Yasser Mustafa",
    description      = "Pipe-chained quantum bound-state solver: Matrix, Numerov, FGH, Salpeter",
    long_description = open("README.md", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    packages         = find_packages(),
    python_requires  = ">=3.8",
    install_requires = ["numpy>=1.21", "scipy>=1.7", "matplotlib>=3.5", "rich>=12.0"],
    classifiers      = [
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
)
