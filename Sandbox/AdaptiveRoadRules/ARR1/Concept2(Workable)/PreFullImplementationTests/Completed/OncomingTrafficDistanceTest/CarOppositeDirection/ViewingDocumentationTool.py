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
# sumoCmd = ['sumo', "-n", "singleRoad.net.xml"]

#   ---   ---   ---   ---

#  Distance of car on oppostie side of road
#
#  Be able to access any or all of the cars
    #  Simply change the colour of any simple characteristic
# 
#  How to determine if car on opposite side of road, would it be the opposite direction on an edge?


import traci

print(dir(traci.vehicle))
# print(help(traci.vehicle.setColor))