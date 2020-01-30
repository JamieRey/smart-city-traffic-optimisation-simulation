#include <iostream>
#include "../Header Files/TraCIClient.h"

int main(int argc, char** argv) {
    std::cout << "Hello, World!" << std::endl;

    TraCIClient client;
    client.connect("localhost", 1337);
    std::cout << "time in s: " << client.simulation.getTime() << "\n";
    std::cout << "run 5 steps ...\n";
    client.simulationStep(5);
    std::cout << "time in s: " << client.simulation.getTime() << "\n";
    client.close();
}