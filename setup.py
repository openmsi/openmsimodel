import setuptools

version = "0.1"

setupkwargs = dict(
    name="openmsimodel",
    version=version,
    description="data modelling package",
    url="https://github.com/openmsi/openmsimodel",
    author="Ali Rachidi",
    author_email="arachid1@jhu.edu",
    # license="MIT",
    # packages=['openmsimodel'],
    packages=setuptools.find_packages(include=["openmsistream*"]),
    # packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": ["gemd_modeller=openmsimodel.utilities.gemd_modeller:main"],
    },
    extras_require={},
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)
