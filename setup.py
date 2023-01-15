from setuptools import setup, find_packages

setup(
    name="lat",
    version="0.1",
    author="Fábio Carneiro, Gabriela Jordão, Miguel Caçador Peixoto",
    author_email="fabiolucas.carneiro@gmail.com, mgabijo@gmail.com, miguelpeixoto457@gmail.com",
    description="Lat: a ply programming language",
    packages=find_packages(),
    install_requires=["ply", "tqdm"],
    entry_points={"console_scripts": ["lat = lat.cli:cli"]},
)
