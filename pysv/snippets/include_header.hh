#include "pybind11/include/pybind11/embed.h"
#include "pybind11/include/pybind11/eval.h"
#include <iostream>
#include <unordered_map>
#include <memory>

// used for ModelSim/Questa to resolve some runtime native library loading issues
// not needed for Xcelium and vcs, but include just in case
#ifdef __linux__
#include <dlfcn.h>
#endif