import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print ("Success")
else:
    print ("Failure")
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/usr/local/Cellar/sumo/1.2.0/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "nodeProximityTest.sumocfg"]

import traci as tr

class VehicleObj:
    def __init__(self, vehicleId):
        self.vehicleId = vehicleId
        # Defining as contant OK because calculated at every step
        self.xPos = tr.vehicle.getPosition(vehicleId)[0]
        self.yPos = tr.vehicle.getPosition(vehicleId)[1]

    def getVehicleId(self):
        return self.vehicleId

    def getXPosCntr(self):
        if self.getDirection() <= 180.0:
            return self.xPos - self.getWidth()
        else:
            return self.xPos + self.getWidth()

    def getYPosCntr(self):
        if self.getDirection() > 180.0:
            return self.yPos - (self.getLength()/2)
        else:
            return self.yPos + (self.getLength()/2)

    def getXPosFrntBumpr(self):
        return self.xPos

    def getYPosFrntBumpr(self):
        return self.yPos

    def getXPosRearBumpr(self):
        if self.getDirection() <= 180.0:
            return self.xPos - self.getWidth()
        else:
            return self.xPos + self.getWidth()

    def getYPosRearBumpr(self):
        if self.getDirection() > 180.0:
            return self.yPos - self.getLength()
        else:
            return self.yPos + self.getLength()

    def getDirection(self):
        return tr.vehicle.getAngle(self.vehicleId)

    def getLength(self):
        return tr.vehicle.getLength(self.vehicleId)

    def getWidth(self):
        return tr.vehicle.getWidth(self.vehicleId)

    def getDistanceToClosestNode(self):
        return

    def setColor(self, color):
        tr.vehicle.setColor(self.vehicleId, color)

    def printInfo(self):
        print(" - VehicleID: ", self.vehicleId, "\n - X Position: ",
              self.xPos, "\n - Y Position: ", self.yPos)


tr.start(sumoCmd)

green = (100, 247, 70)
red = (247, 70, 70)

while tr.simulation.getMinExpectedNumber() > 0:
    tr.simulationStep()
    
    vehicleIds = tr.vehicle.getIDList()

    if len(vehicleIds) > 0:

        vehicleObjs = []

        for vehicleId in vehicleIds:
            #  Determining the cars position
            vhcl = tr.vehicle.getPosition(vehicleId)

            # Save to an array so that comparisons may be made after all
            # information has been gathered
            vehicleObjs.append(VehicleObj(vehicleId))

        vhclsNoOvertake = []

        for i in range(len(vehicleObjs)):
            
            vhcl1 = vehicleObjs[i]

            # List of potentially useful functions
            
            junctionSafeDistance = 12.5
            laneId = tr.vehicle.getLaneID(vhcl1.getVehicleId())
            laneLength = tr.lane.getLength(laneId)
            vhclPstn = tr.vehicle.getLanePosition(vhcl1.getVehicleId())

            if vhclPstn < junctionSafeDistance or vhclPstn > (laneLength - junctionSafeDistance):
                vhcl1.setColor(red)
            else:
                vhcl1.setColor(green)

            # Might have some issues regarding proximity to corners, will cross that
            # bridge when I get to it.

            
print("Simulation Finished")
tr.close()


print("Simulation Finished")
tr.close()
