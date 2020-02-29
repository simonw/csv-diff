from setuptools import setup, find_packages
import io
import os

VERSION = "0.6"


def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="csv-diff",
    description="Python CLI tool and library for diffing CSV files",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    version=VERSION,
    license="Apache License, Version 2.0",
    packages=find_packages(),
    install_requires=["click", "dictdiffer"],
    setup_requires=["pytest-runner"],
    extras_require={"test": ["pytest"]},
    entry_points="""
        [console_scripts]
        csv-diff=csv_diff.cli:cli
    """,
    tests_require=["csv-diff[test]"],
    url="https://github.com/simonw/csv-diff",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
