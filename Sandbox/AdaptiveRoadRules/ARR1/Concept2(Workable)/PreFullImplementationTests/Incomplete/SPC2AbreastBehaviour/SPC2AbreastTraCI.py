import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print("Success")
else:
    print("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")


sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "SPC2Abreast.sumocfg"]

import traci as tr

tr.start(sumoCmd)

while tr.simulation.getMinExpectedNumber() > 0:
    tr.simulationStep()

print("Simulation Finished")
tr.close()
