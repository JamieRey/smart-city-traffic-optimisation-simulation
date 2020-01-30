#ifndef HALF_WIDTH_CAV_TRACICLIENT_H
#define HALF_WIDTH_CAV_TRACICLIENT_H
#include <utils/traci/TraCIAPI.h>

/**
 * This class is responsible for establishing and maintaining a connection to SUMO via the TraCIAPI. This class is
 * expected to be used throughout the program in order to query SUMO about the state of all vehicles within the current
 * simulation and issue commands on how the simulation will progress. Three functions have been implemented on top of
 * the base of this in order to provide much need functionality that is currently missing from the base API. Please
 * refer to the documentation of SUMO and TraCAPI on usage details.
 */

class TraCIClient : public TraCIAPI
{
public:
    TraCIClient() = default;
    ~TraCIClient() = default;
};

#endif