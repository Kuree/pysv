from setuptools import setup
import os


current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='pysv',
    version='0.0.1',
    author='Keyi Zhang',
    author_email='keyi@cs.stanford.edu',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=['pysv'],
    url="https://github.com/Kuree/pysv",
    install_requires=[
        "astor",
    ],
    python_requires=">=3.6",
    extras_require={
        "test": ["numpy", "pytest"]
    }
)
