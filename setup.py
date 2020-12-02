from setuptools import setup
import os
from pathlib import Path


current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, 'README.rst')) as f:
    long_description = f.read()

# search for files to include
package_data = []
for f in Path(os.path.join(current_directory, "pysv")).rglob("*"):
    path = os.path.join(current_directory, f.relative_to(current_directory))
    ext = os.path.splitext(path)[-1]
    if ext in {".cc", ".hh", ".cpp", ".h", ".c", ".txt", ".in", ".cmake", ".sv"} and "test" not in path:
        package_data.append(path)


setup(
    name='pysv',
    version='0.1.2',
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
        "test": ["numpy", "pytest"],
        "test-full": ["tensorflow-cpu", "pytest"]
    },
    package_data={
        "pysv": package_data
    }
)
