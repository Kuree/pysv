# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2023.12.27
### Added
- Add class method returning tuple @AdahilMuniz
- Add support for Python 3.12
- Add support for int array

## [0.2.0] - 2022-08-19
### Added
- Add float datatype

### Fixed
- Fix temp fixture for macos in CI tests
- Fix cmake option to lower the actual requirements

## [0.1.6] - 2021-03-01
### Added
- Add return type reference for multiple return values (#15)

## [0.1.5] - 2021-02-11
### Added
- Add support for cases when `__module__` is None (#12)
- Add support for custom attribute `_source_code_` for classes where are generated from exec (#13)

## [0.1.4] - 2021-02-09
### Fixed
- Improve class type detection, especially for metaclass

## [0.1.3] - 2021-02-04
### Fixed
- Add special logic to detect conda environment (#10)
- Fix pysv deco detection in cases where pysv is used instead of sv

## [0.1.2] - 2020-12-01
### Added
- Add a helper function to force clear imports

## [0.1.1] - 2020-11-30
### Added
- Add guards on imports if it's never used in the code

## [0.1.0] - 2020-11-30
### Added
- Add support for importing types and functions
- Add support for explicit import
- Add documentation
- Add support for Python object as function arguments

### Changed
- Python pointer is changed to public in SV/C++
- Relax restriction on whether sv has been called or not as function decorator

### Fixed
- Minor code generation style fix

## [0.0.5] - 2020-11-21
### Fixed
- For simple compile_and_run, add c++11 flag for old compilers

## [0.0.4] - 2020-11-20
### Added
- Better func_def filtering to figure out proper inputs to the codegen
- Meta information holder for the exported function to be used by other libraries. The variable will not be touch by pysv

### Changed
- str() interface is enhanced to account for various usage types

### Fixed
- arg_to_str will force to convert values to str


## [0.0.3] - 2020-11-19
### Changed
- When code generate binding files, directory will be created automatically if not exist
- CI will upload artifacts

### Fixed
- Python packaging issue


## [0.0.2] - 2020-11-19
### Added
- Auto generated class destructor
- Add ability to automatically detect void return type (#4)
- Add Tensorflow test

### Changed
- Optimize the import (#6)
- Global variables are not represented as unique_ptr to control the tear down process
- Improved foreign module detection

### Fixed
- Occasional crash with Tensorflow
- Python wheel data 

## [0.0.1] - 2020-11-18
Initial release.
### Added
- Complete flow to compile Python to C++ and SystemVerilog bindings as well as shared libraries
- Tested on Linux and MacOS
- Tested with all major commercial simulators as well as Verilator
