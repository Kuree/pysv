#include "Vtest_verilator_array_1d.h"
#include "test_verilator_array_1d.hh"
#include <exception>
#include <random>
#include <iostream>

int main () {
    Vtest_verilator_array_1d vtop;
    vtop.eval();

    // tear down the runtime
    pysv_finalize();
}
