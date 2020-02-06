import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print ("Success")
else:
    print ("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")


sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "oncomingTrafficDistance.sumocfg"]

import traci



# print(dir(traci.route))
# print(dir(traci.simulation))
# print(dir(traci.lane))
# print(dir(traci.junction))
print(dir(traci.edge))
# print(help(traci.vehicle.setColor))