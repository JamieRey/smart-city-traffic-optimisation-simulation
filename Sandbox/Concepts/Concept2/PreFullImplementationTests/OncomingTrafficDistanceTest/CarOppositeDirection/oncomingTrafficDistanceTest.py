
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
sumoCmd = [sumoBinary, "-c", "TestOncomingTrafficDistance.sumocfg"]

import traci as tr

green = (100, 247, 70)
red = (247, 70, 70)

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

    def setColor(self, color):
        tr.vehicle.setColor(self.vehicleId, color)

    def printInfo(self):
        print(" - VehicleID: ", self.vehicleId, "\n - X Position: ",
              self.xPos, "\n - Y Position: ", self.yPos)


def isCarInfront(vhclObj1, vhclObj2):

    vhcl1FrntX = vhclObj1.getXPosFrntBumpr()
    vhcl1FrntY = vhclObj1.getYPosFrntBumpr()

    vhcl1RearX = vhclObj1.getXPosRearBumpr()
    vhcl1RearY = vhclObj1.getYPosRearBumpr()

    vhcl2FrntX = vhclObj2.getXPosFrntBumpr()
    vhcl2FrntY = vhclObj2.getYPosFrntBumpr()

    vhcl2RearX = vhclObj2.getXPosRearBumpr()
    vhcl2RearY = vhclObj2.getYPosRearBumpr()

    frntTofrntDist = math.sqrt(
        (vhcl1FrntX - vhcl2FrntX)**2 + (vhcl1FrntY - vhcl2FrntY)**2)
    rearTorearDist = math.sqrt(
        (vhcl1RearX - vhcl2RearX)**2 + (vhcl1RearY - vhcl2RearY)**2)

    if frntTofrntDist < rearTorearDist:
        return 1
    elif frntTofrntDist == rearTorearDist:
        return 0
    elif frntTofrntDist > rearTorearDist:
        return -1
    else:
        return -2


def isCarTravelingInOppositeDirection(vhclObj1, vhclObj2):
    if vhcl1.getDirection() == vhcl2.getDirection():
        return False
    else:
        return True


tr.start(sumoCmd)

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
            for j in range(i+1, len(vehicleObjs)):
                # Once all positions are gathered, determine if any cars are
                # suitable to begin overtake
                vhcl1 = vehicleObjs[i]
                # vhcl1Id = vhcl1.getVehicleId()
                vhcl1xC = vhcl1.getXPosFrntBumpr()
                vhcl1yC = vhcl1.getYPosFrntBumpr()

                vhcl2 = vehicleObjs[j]
                # vhcl2Id = vhcl2.getVehicleId()
                vhcl2xC = vhcl2.getXPosFrntBumpr()
                vhcl2yC = vhcl2.getYPosFrntBumpr()

                safeToOvertake = None
                safeDistance = 15
                # TODO Accurately calculate Safe Distance
                # print("getHeight: ",tr.vehicle.getHeight(vehicleId))
                # print("getLength: ",tr.vehicle.getLength(vehicleId))
                # getLanePosition: "The position of the vehicle along the lane measured in m."
                carAreas = math.sqrt(
                    ((vhcl2xC - vhcl1xC)**2) + ((vhcl2yC - vhcl1yC)**2))

                # Car NOT within geo-fence
                if carAreas >= 2*safeDistance:
                    vhcl1.setColor(green)
                    vhcl2.setColor(green)
                # Car within geo-fence
                else:
                    # Is on same side of road?
                    if isCarTravelingInOppositeDirection(vhcl1, vhcl2):
                        # It's not on the same side
                        # Has the car passed me yet?
                        if isCarInfront(vhcl1, vhcl2) == -1:
                            # It's passed
                            vhcl1.setColor(green)
                            vhcl2.setColor(green)
                        else:
                            # It hasn't yet passed
                            # Comparing every value can cause overwrites, whereby cars the shouldn't be allowed
                            # to overtake, and then granted the ability to do so when its unsafe to do so
                            vhclsNoOvertake.append(vhcl1)
                            vhclsNoOvertake.append(vhcl2)
                    else:
                        # It's on the same side
                        vhcl2.setColor(green)
                        vhcl1.setColor(green)

        for vhcl in vhclsNoOvertake:
            vhcl.setColor(red)

print("Simulation Finished")
tr.close()
