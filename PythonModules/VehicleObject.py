# -----------------------------------------------------------
# Using Adaptive Road Rules & Single Person Vehicles to Optimise Traffic Flow
#
# (C) 2020 James Reynolds, Manchester, United Kingdom
# Email Jamie.rpr@gmail.com
# -----------------------------------------------------------

import traci as tr
import math

""""
An convient means of getting and setting vehicle variables to keep code dry.

Contains INBUILT TraCI functions to and CUSTOM functions.

CUSTOM FUNCTION:
    getXYPosCntr()
    getXYPosRear()
"""

class VehicleObj:
    def __init__(self, vehicleId):
        self.vehicleId = vehicleId

    # Vehicle Meta

    def getVehicleId(self):
        return self.vehicleId

    def getVehicleType(self):
        return tr.vehicle.getTypeID(self.vehicleId)

    def setVehicleType(self, className):
        tr.vehicle.setType(self.vehicleId, className)
    
    def getVehicleClass(self):
        return tr.vehicle.getVehicleClass(self.vehicleId)

    def setColor(self, color):
        tr.vehicle.setColor(self.vehicleId, color)

    # Vehicle Lane 

    def getLaneID(self):
        return tr.vehicle.getLaneID(self.vehicleId)

    def getLanePosition(self):
        return tr.vehicle.getLanePosition(self.vehicleId)

    def moveToLane(self,laneID,pos):
        tr.vehicle.moveTo(self.vehicleId,laneID, pos)

    # Vehicle Dimensions

    def getLength(self):
        return tr.vehicle.getLength(self.vehicleId)

    def getWidth(self):
        return tr.vehicle.getWidth(self.vehicleId)

    # Vehicle speed and direction

    def getSpeed(self):
        return tr.vehicle.getSpeed(self.vehicleId)

    def getDirection(self):
        return self.roundTen(tr.vehicle.getAngle(self.vehicleId))
    
    # Vehicle Positions

    def getXYPosFrnt(self):
        """
        Returns the (x,y) position of the vehicles FRONT bumper. 
        """
        return (tr.vehicle.getPosition(self.vehicleId)[0], tr.vehicle.getPosition(self.vehicleId)[1])

    def getXYPosCntr(self):
        """
        Returns the (x,y) position of the vehicles CENTER.
        """
        carFrontX = self.getXYPosFrnt()[0]
        carFrontY = self.getXYPosFrnt()[1]
        carDirectionOfTravel = self.getDirection()
        adjustedCarDirectionOfTravel = -1

        # Converting the angel
        if carDirectionOfTravel <= 90.0:
            adjustedCarDirectionOfTravel = (carDirectionOfTravel - 90) * -1
        elif carDirectionOfTravel > 90.0 and carDirectionOfTravel <= 180.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 180) * -1) + 270
        elif carDirectionOfTravel > 180.0 and carDirectionOfTravel <= 270.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 270) * -1) + 180
        elif carDirectionOfTravel > 270.0 and carDirectionOfTravel <= 360.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 360) * -1) + 90

        carDirectionOfTravelRadians = adjustedCarDirectionOfTravel * math.pi / 180.0
        carLength = self.getLength()/2

        carMidY = 0.0
        carMidX = 0.0

        if adjustedCarDirectionOfTravel < 90.0:
            carMidX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carMidY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 90.0 and adjustedCarDirectionOfTravel < 180.0:
            carMidX = carFrontX + carLength * math.cos(carDirectionOfTravelRadians)
            carMidY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 180.0 and adjustedCarDirectionOfTravel < 270.0:
            carMidX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carMidY = carFrontY + carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 270.0 and adjustedCarDirectionOfTravel <= 360.0:
            carMidX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carMidY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)

        return (carMidX, carMidY)

    def getXYPosRear(self):
        """
        Returns the (x,y) position of the vehicles REAR bumper.
        """
        carFrontX = self.getXYPosFrnt()[0]
        carFrontY = self.getXYPosFrnt()[1]
        carDirectionOfTravel = self.getDirection()
        adjustedCarDirectionOfTravel = -1

        # Converting the angel
        if carDirectionOfTravel <= 90.0:
            adjustedCarDirectionOfTravel = (carDirectionOfTravel - 90) * -1
        elif carDirectionOfTravel > 90.0 and carDirectionOfTravel <= 180.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 180) * -1) + 270
        elif carDirectionOfTravel > 180.0 and carDirectionOfTravel <= 270.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 270) * -1) + 180
        elif carDirectionOfTravel > 270.0 and carDirectionOfTravel <= 360.0:
            adjustedCarDirectionOfTravel = ((carDirectionOfTravel - 360) * -1) + 90

        carDirectionOfTravelRadians = adjustedCarDirectionOfTravel * math.pi / 180.0
        carLength = self.getLength()

        carRearY = 0
        carRearX = 0

        if adjustedCarDirectionOfTravel < 90.0:
            carRearX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carRearY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 90.0 and adjustedCarDirectionOfTravel < 180.0:
            carRearX = carFrontX + carLength * math.cos(carDirectionOfTravelRadians)
            carRearY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 180.0 and adjustedCarDirectionOfTravel < 270.0:
            carRearX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carRearY = carFrontY + carLength * math.sin(carDirectionOfTravelRadians)
        elif adjustedCarDirectionOfTravel >= 270.0 and adjustedCarDirectionOfTravel <= 360.0:
            carRearX = carFrontX - carLength * math.cos(carDirectionOfTravelRadians)
            carRearY = carFrontY - carLength * math.sin(carDirectionOfTravelRadians)

        return (carRearX, carRearY)

    # Utility Function

    def roundTen(self,n): 
        # Smaller multiple 
        a = (n // 10) * 10
        # Larger multiple 
        b = a + 10
        # Return of closest of two 
        return (b if n - a > b - n else a) 