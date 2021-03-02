#include "Vtest_verilator_return_ref.h"
#include "test_verilator_return_ref.hh"
#include <exception>
#include <random>
#include <iostream>

int main () {
    Vtest_verilator_return_ref vtop;
    set_value(&vtop.a, &vtop.b);
    vtop.eval();
    if (vtop.a != 42) {
        throw std::runtime_error("error");
    }
    if (vtop.b != 43) {
        throw std::runtime_error("error");
    }
    if (vtop.c != (42 + 43)) {
        throw std::runtime_error("error");
    }

    // tear down the runtime
    pysv_finalize();
}
