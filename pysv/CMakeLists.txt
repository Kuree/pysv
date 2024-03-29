cmake_minimum_required(VERSION 3.4)
set(CMAKE_CXX_STANDARD 11)
project(${TARGET})

add_subdirectory(pybind11)

if (APPLE)
    pybind11_add_module(${TARGET} SHARED ${TARGET}.cc)
else()
    pybind11_add_module(${TARGET} MODULE ${TARGET}.cc)
endif()

target_link_libraries(${TARGET} PRIVATE pybind11::embed)

# include the sv lib directory
target_include_directories(${TARGET} PRIVATE ${DPI_HEADER_DIR})

set(SHARED_LIB_EXT ".so")

add_definitions(-DPYTHON_LIBRARY="${PYTHON_LIBRARY}")

# use the default system suffix
set_target_properties(${TARGET} PROPERTIES PREFIX ""
        SUFFIX ${SHARED_LIB_EXT})

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    set_target_properties(${TARGET} PROPERTIES COMPILE_FLAGS -fsized-deallocation)
endif()
