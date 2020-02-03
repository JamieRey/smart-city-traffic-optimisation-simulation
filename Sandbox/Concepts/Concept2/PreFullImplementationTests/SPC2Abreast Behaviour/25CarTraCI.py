import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print ("Success")
else:
    print ("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "config25car.sumocfg"]

import traci

traci.start(sumoCmd)

carId = 0



while carId < 25 :
    traci.vehicle.setColor("1", (255, 10, 97, 1))
    carId += 1

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    print(traci.vehicle.getIDList())

print("Simulation Finished")
traci.close()
