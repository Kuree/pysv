# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.0.3] - 2020-11-19
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
