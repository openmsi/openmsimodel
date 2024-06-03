import setuptools

version = "0.1.6"

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setupkwargs = dict(
    name="openmsimodel",
    version=version,
    description="OpenMSIModel uses the GEMD (Graphical Expression of Material Data) format to interact with generalized laboratory, analysis, and computational materials data. It allows to structure real scientific workflows into meaningful data structures, model them in graph and relational databases, explore on interactive graphical interfaces, and build long-term, shareable assets stores.",
    url="https://github.com/openmsi/openmsimodel",
    author="Ali Rachidi",
    author_email="arachid1@jhu.edu",
    license="MIT",
    packages=setuptools.find_packages(include=["openmsimodel*"]),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "open_db=openmsimodel.db.open_db:main",
            "open_graph=openmsimodel.graph.open_graph:main",
        ]
    },
    python_requires=">=3.7,<3.10",
    install_requires=requirements,
    extras_require={},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)
