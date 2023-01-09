from setuptools import setup, find_packages

setup(
    name='tox',
    version='0.1',
    author='Fábio Carneiro',
    author_email='fabiolucas.carneiro@gmail.com',
    description='Tox: a ply programming language',
    packages=find_packages(),
    install_requires=[
        'ply',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'tox = tox.cli:cli'
        ]
    }
)