#include "Vbox_filter.h"
#include "box_filter.hh"
#include <exception>
#include <random>
#include <iostream>

int main () {
    Vbox_filter vtop;
    pysv::BoxFilter model(4);

    vtop.clk = 0;
    vtop.rst = 0;
    vtop.eval();

    vtop.rst = 1;
    vtop.eval();
    vtop.rst = 0;
    vtop.eval();

    // initialize the random
    std::random_device rd;
    std::mt19937 gen(0);
    std::uniform_int_distribution<uint32_t> distrib(0, 0xFFFF);

    for (int i = 0; i < 100; i++) {
        int value = distrib(gen);
        vtop.in = value;
        model.push(value);

        vtop.eval();
        vtop.clk = 1;
        vtop.eval();


        uint32_t avg = model.avg();
        uint32_t sv = vtop.out;
        if (sv != avg) {
            std::cerr << "[" << i << "] model: " << avg << " SV: " << sv << std::endl;
            throw std::runtime_error("Incorrect SV!");
        }

        vtop.clk = 0;
        vtop.eval();
    }

    // tear down the runtime
    pysv_finalize();
}