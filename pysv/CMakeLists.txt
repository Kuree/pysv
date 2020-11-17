cmake_minimum_required(VERSION 3.4)
set(CMAKE_CXX_STANDARD 11)
project(${TARGET})

add_subdirectory(pybind11)

# this is to avoid glibc++ mismatch between the ones shipped with the simulator
# and the one you're currently using. only valid for Linux since most EDA tools only
# work on Linux
if(UNIX AND NOT APPLE)
    set(STATIC_FLAG "-static-libgcc -static-libstdc++")
    set(CMAKE_CXX_FLAGS "-Wl,--whole-archive -Wl,--no-whole-archive -lgcc -lstdc++")
endif()

pybind11_add_module(${TARGET} SHARED ${TARGET}.cc)

target_link_libraries(${TARGET} PUBLIC ${STATIC_FLAG})
target_link_libraries(${TARGET} PRIVATE pybind11::embed)

set(SHARED_LIB_EXT ".so")

# use the default system suffix
set_target_properties(${TARGET} PROPERTIES PREFIX ""
        SUFFIX ${SHARED_LIB_EXT})

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    set_target_properties(${TARGET} PROPERTIES COMPILE_FLAGS -fsized-deallocation)
endif()
