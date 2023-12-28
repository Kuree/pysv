#include "Vtest_verilator_array.h"
#include "test_verilator_array.hh"
#include <exception>
#include <random>
#include <iostream>

int main () {
    Vtest_verilator_array vtop;
    vtop.eval();

    // tear down the runtime
    pysv_finalize();
}
