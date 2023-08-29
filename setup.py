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
    packages=setuptools.find_packages(include=["openmsimodel*"]),
    # packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "open_graph=openmsimodel.graph.open_graph:main",
            "open_db=openmsimodel.db.open_db:main",
        ],
    },
    python_requires=">=3.7,<3.10",
    install_requires=[
        "gemd",
        "methodtools",
        "pandas",
    ],
    extras_require={},
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)
