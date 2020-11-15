from setuptools import setup

desc = \
    """
pysv is a library that allow SV test generators work with Python functional models natively
    """

setup(
    name='pysv',
    version='0.0.1',
    author='Keyi Zhang',
    author_email='keyi@cs.stanford.edu',
    description=desc,
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
