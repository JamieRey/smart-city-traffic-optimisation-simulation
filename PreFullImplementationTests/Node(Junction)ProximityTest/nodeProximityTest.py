# -----------------------------------------------------------
# Using Adaptive Road Rules & Single Person Vehicles to Optimise Traffic Flow
#
# (C) 2020 James Reynolds, Manchester, United Kingdom
# Email Jamie.rpr@gmail.com
# -----------------------------------------------------------

import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print ("Success")
else:
    print ("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "SUMO/nodeProximityTest.sumocfg"]

import traci as tr
sys.path.insert(1, "../../PythonModules")
from VehicleObject import VehicleObj
import VehicleMethods as vhclMthds

tr.start(sumoCmd)

green = (100, 247, 70)
red = (247, 70, 70)

while tr.simulation.getMinExpectedNumber() > 0:
    tr.simulationStep()
    
    vehicleIds = tr.vehicle.getIDList()

    if len(vehicleIds) > 0:

        vehicleObjs = []
        for vehicleId in vehicleIds:
            vehicleObjs.append(VehicleObj(vehicleId))

        for vhcl in vehicleObjs:
            if vhclMthds.isWithinJunctionProximity(vhcl, 12.5, "SUMO/junctionProximityTest.net.xml"):
                vhcl.setColor(red)
            else:
                vhcl.setColor(green)

print("Simulation Finished")
tr.close()