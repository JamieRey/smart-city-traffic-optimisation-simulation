# -----------------------------------------------------------
# Using Adaptive Road Rules & Single Person Vehicles to Optimise Traffic Flow
#
# (C) 2020 James Reynolds, Manchester, United Kingdom
# Email Jamie.rpr@gmail.com
# -----------------------------------------------------------

import os
import sys
import math

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print("Success")
else:
    print("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")


sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "SUMO/SPCACLanePermissions.sumocfg"]

import traci as tr
sys.path.insert(1, "../../PythonModules")
from VehicleObject import VehicleObj
import VehicleMethods as vhclMthds

green = (100, 247, 70)
red = (247, 70, 70)

tr.start(sumoCmd)

while tr.simulation.getMinExpectedNumber() > 0:

    AVhcls = []
    AVhclsNoSPC = []
    SPCS = []
    SPCOS = []

    vhclsOvertake = []
    vhclsNoOvertake = []
    vhclIds = tr.vehicle.getIDList() 

    if len(vhclIds) > 0:

        for vhclId in vhclIds:
            vhcl = VehicleObj(vhclId)
            
            AVhcls.append(vhcl)

            if vhcl.getVehicleType() == "SPC":
                SPCS.append(vhcl)
                vhcl.setColor(orange)
            elif vhcl.getVehicleType() == "SPCO":
                SPCOS.append(vhcl)
                vhcl.setColor(green)
            else:
                AVhclsNoSPC.append(VehicleObj(vhclId))

        for SPC in SPCS:
            vhclMthds.canVhclOvertake(SPC, AVhcls, "SUMO/CorrectLaneMigration.net.xml")

        for SPCO in SPCOS:
            vhclMthds.canVhclRtrnToLane(SPCO, AVhcls, "SUMO/CorrectLaneMigration.net.xml")

    tr.simulationStep()
            
print("Simulation Finished")
tr.close()