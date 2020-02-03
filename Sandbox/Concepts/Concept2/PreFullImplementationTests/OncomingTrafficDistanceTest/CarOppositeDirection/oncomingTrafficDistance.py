import os, sys, math

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print ("Success")
else:
    print ("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")


sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "oncomingTrafficDistance.sumocfg"]
# sumoCmd = ['sumo', "-c", "oncomingTrafficDistance.sumocfg"]

#   ---   ---   ---   ---

#  Distance of car on oppostie side of road
#
#  !DONE! Be able to access any or all of the cars !DONE!
    # !DONE! Simply change the colour of any simple characteristic !DONE!

import traci as tr

green = (100, 247, 70)
red = (247, 70, 70)

class VehiclePosition:
    def __init__(self, vehicleId, xPos, yPos):
        self.vehicleId = vehicleId
        self.xPos = xPos
        self.yPos = yPos
    
    def getVehicleId(self):
        return self.vehicleId

    def getXPos(self):
        return self.xPos

    def getYPos(self):
        return self.yPos

    def getDirection(self):
        return tr.vehicle.getAngle(self.vehicleId)

    def setColor(self, color):
        tr.vehicle.setColor(self.vehicleId, color)

    def printInfo(self):
        print(" - VehicleID: ", self.vehicleId, "\n - X Position: ", self.xPos, "\n - Y Position: ", self.yPos)




tr.start(sumoCmd)

while tr.simulation.getMinExpectedNumber() > 0:
    
    tr.simulationStep()

    vehicleIds = tr.vehicle.getIDList()

    if len(vehicleIds) > 0:

        vehiclesPositions = []

        for vehicleId in vehicleIds:
            # Identifying the vehicle
            # print("\n -- -- -- -- -- --")
            # print("VehicleID:", vehicleId)

            #  Determining the cars position
            vp = tr.vehicle.getPosition(vehicleId)

            # Save to an array so that comparisons may be made after all 
            # information has been gathered
            vpObj = VehiclePosition(vehicleId, vp[0], vp[1])
            vehiclesPositions.append(vpObj)

        # print("Total # Vehicle Position: ", len(vehiclesPositions))

        for i in range(len(vehiclesPositions)):
            for j in range(i+1, len(vehiclesPositions)):
                # Once all positions are gathered, determine if any cars are 
                # suitable to begin overtake
                vp1 = vehiclesPositions[i]
                # vp1Id = vp1.getVehicleId()
                vp1x = vp1.getXPos()
                vp1y = vp1.getYPos()
                
                vp2 = vehiclesPositions[j]
                # vp2Id = vp2.getVehicleId()
                vp2x = vp2.getXPos()
                vp2y = vp2.getYPos()

                safeToOvertake = None
                safeDistance = 20
                # TODO Accurately calculate Safe Distance
                # print("getHeight: ",tr.vehicle.getHeight(vehicleId))
                # print("getLength: ",tr.vehicle.getLength(vehicleId))
                carAreas = math.sqrt(((vp2x - vp1x)**2) + ((vp2y - vp1y)**2))

                # Is car within geo-fence
                if carAreas >= 2*safeDistance:
                    vp1.setColor(green)
                    vp2.setColor(green)
                else:
                    vp1.setColor(red)
                    vp2.setColor(red)

                # Is car going the opposite OR same direction
                print(vp1.getDirection())
                print(vp2.getDirection())

                # vp1Velocity = math.sqrt(vp1x**2 + vp1y**2)
                # vp2Velocity = math.sqrt(vp2x**2 + vp2y**2)

                # if 


                

                

# getLateralAlignment

            # print("getLaneID: ",tr.vehicle.getLaneID(vehicleId))
            # print("getLaneIndex: ",tr.vehicle.getLaneIndex(vehicleId))
            
            
            # print("getRoadID: ",tr.vehicle.getRoadID(vehicleId))
            # print("getSpeed: ",tr.vehicle.getSpeed(vehicleId))
            # print("getLanePosition: ",tr.vehicle.getLanePosition(vehicleId))
        # print(" -- -- -- -- -- --")


print("Simulation Finished")
tr.close()
