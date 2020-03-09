import io
import re

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="UTF-8") as f:
    readme = f.read()

with io.open('src/papilotte/__init__.py', 'rt', encoding='utf-8') as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)


setup(
    name="Papilotte",
    version=version,
    url="https://github.com/gvasold/papilotte/",
    project_urls = {
    #    "Dokumentation": "TODO",
        "Code": "https://github.com/gvasold/papilotte/",
        "Issue tracker": "https://github.com/gvasold/papilotte/issues",
    },
    license="Apache License Version 2.0",
    author="Gunter Vasold",
    author_email="gunter.vasold@gmail.com",
    description="A flexible server and proxy for prosopographical data.",
    long_description=readme,
    # TODO: add classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"

    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["openapi/*yml", "config/*yml"]},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
	"werkzeug==0.15.6", # remove after upgrading to next connexion version
        "swagger-ui-bundle==0.0.5", # set to >= after connexion upgrade
        "connexion==2.3.0",
        "strict-rfc3339",
        "pytz>=2019.3",
        "toml",
        "voluptuous",
        "pony==0.7.11"
    ],
    extras_require={
        "dev": [
            "pytest",
            "coverage",
            "tox",
        ]
    },
    entry_points={"console_scripts": ["papilotte = papilotte.cli:main"]},
)
