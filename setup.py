from setuptools import setup, find_packages

setup(
    name="openmsimodel",
    version="0.1",
    description="data modelling package",
    url="http://github.com/storborg/funniest",
    author="Ali Rachidi",
    author_email="arachid1@jhu.edu",
    license="MIT",
    # packages=['openmsimodel'],
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": ["gemd_modeller=openmsimodel.utilities.gemd_modeller:main"],
    },
)
