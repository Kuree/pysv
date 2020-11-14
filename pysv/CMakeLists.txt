cmake_minimum_required(VERSION 3.0)
set(CMAKE_CXX_STANDARD 11)
project(${TARGET})

add_subdirectory(pybind11)

# this is to avoid glibc++ mismatch between the ones shipped with the simulator
# and the one you're currently using
set(STATIC_FLAG "-static-libgcc -static-libstdc++")
set(CMAKE_CXX_FLAGS "-Wl,--whole-archive -Wl,--no-whole-archive -lgcc -lstdc++")

pybind11_add_module(${TARGET} ${TARGET}.cc)

target_link_libraries(${TARGET} PUBLIC ${STATIC_FLAG})
target_link_libraries(${TARGET} PRIVATE pybind11::embed)
# use the default system suffix
set_target_properties(${TARGET} PROPERTIES PREFIX ""
        SUFFIX ".so")

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    set_target_properties(${TARGET} PROPERTIES COMPILE_FLAGS -fsized-deallocation)
endif()
