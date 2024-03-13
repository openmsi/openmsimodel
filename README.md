# openmsimodel
[![PyPI](https://img.shields.io/pypi/v/openmsimodel)](https://pypi.org/project/openmsimodel/) [License](https://img.shields.io/github/license/openmsi/openmsimodel) 
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openmsimodel) 
![CircleCI](https://img.shields.io/circleci/build/github/openmsi/openmsistream/main) [![Documentation Status](https://readthedocs.org/projects/openmsimodel/badge/?version=latest)](https://openmsimodel.readthedocs.io/en/latest/?badge=latest) 


OpenMSIModel uses the GEMD (Graphical Expression of Material Data) format to interact with generalized laboratory, analysis, and computational materials data.
It allows to structure real scientific workflows into meaningful data structures, model them in graph and relational databases, explore on interactive graphical interfaces, and build long-term, shareable assets stores.

Available on PyPI at https://pypi.org/project/openmsimodel and GitHub at https://github.com/openmsi/openmsimodel

Official documentation at https://openmsimodel.readthedocs.io/en/latest/

## Installation:

```
pip install openmsimodel
```

for Mac Users:

```
brew install graphviz
python -m pip install \
    --global-option=build_ext \
    --global-option="-I$(brew --prefix graphviz)/include/" \
    --global-option="-L$(brew --prefix graphviz)/lib/" \
    pygraphviz
pip install openmsimodel
```
