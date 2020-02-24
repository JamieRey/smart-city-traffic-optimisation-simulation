# -----------------------------------------------------------
# Using Adaptive Road Rules & Single Person Vehicles to Optimise Traffic Flow
#
# (C) 2020 James Reynolds, Manchester, United Kingdom
# Email Jamie.rpr@gmail.com
# -----------------------------------------------------------

import math, traci as tr, sumolib
from VehicleObject import VehicleObj

# TODO
junctionProximitySafetyDistance = 10
minimumProximityForOvertaking = 12
avProximityDistance = 50
returningToLaneSafeDistance = 10
safeOvertakingDistance = 50

"""
This module contains functions which aid vehicles in:
    - Overtaking
    - Safely returning to a lane
    - Detecing relative vehicle proximity and class
    - Junction proximity

    Keywords
    --------
    SPC  : Single Person Car (not overtaking)
    SPCO : Single Person Car Overtaking 
    AV   : Any Vehicle (Not an SPC or SPCO)
"""

# Checking vehicle arrays for specific vehicle types

def anyAV(vhclArray):
    """
    Check Array for AV

    Checks an array of vehicles, and confirms whether it contains an AV type vehicle.

    Parameters
    ----------
    vhclArray : array(VehicleObject)

    Returns
    -------
    Boolean
        Array contains an AV - True
        Array doesn't contain an AV - False
    """
    if not anySPC(vhclArray) and not anySPCO(vhclArray):
        return True
    else:
        return False


def anySPC(vhclArray):
    """
    Check Array for SPC

    Checks an array of vehicles, and confirms whether it contains an SPC type vehicle.

    Parameters
    ----------
    vhclArray : array(VehicleObject)

    Returns
    -------
    Boolean
        Array contains an SPC - True
        Array doesn't contain an SPC - False
    """
    responce = False
    for vhcl in vhclArray:
        if vhcl.getVehicleType() == "SPC":
            responce = True

    return responce

def anySPCO(vhclArray):
    """
    Check Array for SPCO

    Checks an array of vehicles, and confirms whether it contains an SPCO type vehicle.

    Parameters
    ----------
    vhclArray : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : Array contains an SPCO 
        False : Array doesn't contain an SPCO
    """
    responce = False
    for vhcl in vhclArray:
        if vhcl.getVehicleType() == "SPCO":
            responce = True

    return responce

# Filtering vehicle arrays

def getAVhclsNoSPC(vhclArray):
    """
    Just AV Type From Array

    Takes any AV vehicles from an array of vehicles, adds them to an array, and returns the array.

    Parameters
    ----------
    vhclArray : array(VehicleObject)

    Returns
    -------
    array(VehicleObject)
        The array will only contain AV type vehicles.
    """
    vhclsToRtn=[]
    for vhcl in vhclArray:
        if not isAnySPC(vhcl):
            vhclsToRtn.append(vhcl)
    return vhclsToRtn

# Checking indavidual vehicles type

def isAnySPC(vhcl):
    """
    Is Vehicle SPC/SPCO

    Takes a vehicle, and checks whether it's and SPC or SPCO.

    Parameters
    ----------
    vhcl : VehicleObject

    Returns
    -------
    Boolean
        True  : The vehicles IS either an SPC or SPCO
        False : The vehicles IS NOT either an SPC or SPCO
    """
    if vhcl.getVehicleType() == "SPC" or vhcl.getVehicleType() == "SPCO":
        return True
    else:
        return False

# Lane Changing

def moveToOvertakingLane(vhcl, netPath):
    """
    Moves To Overtaking Lane

    Checks if destination lane isn't a special lane, and whether the vehicle isn't already overtaking
    and then move the vehicle to the correct lane and changes its class to SPCO

    Parameters
    ----------
    vhcl : VehicleObject
    netPath : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    None

    """
    if isSpecialEdge(vhcl, netPath): # Some lanes are "special", and are unable to support vehicles
        return
    elif vhcl.getVehicleType() == "SPCO":
        print("WARNING: Vehicle already in correct lane [0]")
    elif vhcl.getVehicleType() == "SPC":
        vhcl.setVehicleType("SPCO")
        
        trgLnID = vhcl.getLaneID()[:-1] + "1" # Overtaking lanes all end with a "1"
        trgLnPs = vhcl.getLanePosition()
        vhcl.moveToLane(trgLnID, trgLnPs)
        tr.simulation.step() # A step must be trigered to update the ID lists

def moveToNonOvertakingLane(vhcl, netPath):
    """
    Moves To Non-Overtaking Lane

    Checks if destination lane isn't a special lane, and whether the vehicle isn't already an SPC
    and then move the vehicle to the correct lane and changes its class to SPC

    Parameters
    ----------
    vhcl : VehicleObject
    netPath : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    None
    """
    if isSpecialEdge(vhcl, netPath): # Some lanes are "special", and are unable to support vehicles
        return
    elif vhcl.getVehicleType() == "SPC":
        print("WARNING: Vehicle already in correct lane [1]")
    elif vhcl.getVehicleType() == "SPCO":
        vhcl.setVehicleType("SPC")

        trgLnID = vhcl.getLaneID()[:-1] + "0" # Non-overtaking lanes all end with a "0"
        trgLnPs = vhcl.getLanePosition()
        vhcl.moveToLane(trgLnID, trgLnPs)
        tr.simulation.step() # A step must be trigered to update the ID lists

def isSpecialEdge(vhcl, netPath):
    """
    Special Lane Detection

    Some lanes in SUMO are "special" and are used for rendering and internal purposes. These lanes cannot support 
    traffic and so checks must be made.

    Parameters
    ----------
    vhcl : VehicleObject
    netPath : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    Boolean
        True : Vhcls is on a "special" edge
        False : Vhcls is NOT on a "special" edge
    """

    net = sumolib.net.readNet(netPath, withInternal=True)
    specialEdges = []

    # Gather all special edges
    for edge in net.getEdges(True):
        if edge.isSpecial():
            specialEdges.append(edge.getID())

    # Is vehicle on a special edge
    if tr.lane.getEdgeID(vhcl.getLaneID()) in specialEdges:
        return True
    else:
        return False

# Determining if car can overtake

def canVhclOvertake(vhclMain, allVhcls, netPath):
    """
    Move to Overtaking Lane

    Determines whether it is safe to overtake, and whether the 
    vehicles should overtake, and if so forces the vehicle to overtake

    Parameters
    ----------
    vhclMain : VehicleObject
    allVhcls : array(VehicleObject)
    netPath  : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    Boolean
        True  : Vehicle did overtake
        False : Vehicle did NOT overtake 
    """

    # Making sure all updated vehicles are present
    allVhcls = []
    vhclIds = tr.vehicle.getIDList()

    for vhclId in vhclIds:
        vhcl = VehicleObj(vhclId)
        allVhcls.append(vhcl)

    if vhclMain in allVhcls:
        allVhcls.remove(vhclMain)

    # Gathering whether there are vehicles are in proximity, and collecting cars within proximity into an array
    carPrxmtyTest = carWithinProximity(vhclMain, allVhcls, safeOvertakingDistance)
    isCarInPrxmty = carPrxmtyTest[0]
    carsWithinProximity = carPrxmtyTest[1]

    isWithinJunctionPrx = isWithinJunctionProximity(vhclMain, junctionProximitySafetyDistance, netPath)

    if not isWithinJunctionPrx: # Vehicle can't be too close to junction, as it would be unsafe

        oppstJunctnInProximity = distanceOfOppositeJunction(vhclMain, 45, netPath)

        if oppstJunctnInProximity: # Vehicle can't be too close to junction, as it would be unsafe
            return False

        if isCarInPrxmty: 

            # Gather vehicles traveling the opposite direction, and of those, the ones infront of the current vehicle
            vhclsAreTrvlngOppstDr = areVhclsTrvlngOppstDir(vhclMain, carsWithinProximity)
            vhclOppDr = getVhclsTrvlngOppstDir(vhclMain, carsWithinProximity)        
            vhclsTrvlngOppstDir = getVhclsInfrnt(vhclMain, vhclOppDr)
        
            if vhclsAreTrvlngOppstDr:
                if anyAV(vhclsTrvlngOppstDir):

                    if isAvTooClose(vhclMain, vhclsTrvlngOppstDir): # If AV on opposite side is too close SPCO will collide with it
                        return False

                    # Safely Changes opposing SPC's into SPCO's
                    elif anySPC(vhclsTrvlngOppstDir):
                        if anyVhcls2Abreast(vhclsTrvlngOppstDir): # If vehicles are 2 abreast they will collide when changing lane
                            return False
                        else:
                            for SPC in vhclsTrvlngOppstDir:
                                moveToOvertakingLane(SPC, netPath) # Change SPC into SPCO
                            return True
                else: # No AV on opposite side

                    # Safely Changes opposing SPC's into SPCO's
                    if anySPC(vhclsTrvlngOppstDir):
                        if anyVhcls2Abreast(vhclsTrvlngOppstDir): # If vehicles are 2 abreast they will collide when changing lane
                            return False
                        else:
                            for SPC in vhclsTrvlngOppstDir: 
                                moveToOvertakingLane(SPC, netPath) # Change SPC into SPCO
                            return True
                    else:
                        # Only SPCOs on opposite side of road
                        return True
                        
            
            # Gather vehicles traveling the same direction for checks
            vhclsAreTrvlngSameDr = areVhclsTrvlngSameDir(vhclMain, carsWithinProximity)
            vhclsTrvlngSmeDr = getVhclsTrvlngSameDir(vhclMain, carsWithinProximity)

            if vhclsAreTrvlngSameDr:
                if isVhclInfntAV(vhclMain, vhclsTrvlngSmeDr): # So that only AV is overtaken, and not other SPC

                    # Prevents SPC colliding into each other when overtaking
                    vhclToLeft = isVehicleToTheLeft(vhclMain, vhclsTrvlngSmeDr) 
                    if vhclToLeft:
                        return False
                    elif not vhclToLeft:
                        moveToOvertakingLane(vhclMain, netPath)
                        return True
                    else:
                        return False

        else: # No vehicles in range
            return False
    else: # Car within junction proximity
        return False

    return False
    
def isAvTooClose(vhcl, vhclArray):
    """
    Check AV Proximity

    Checks the closest AV's proximity to the vehicle is above a safe distance.

    Parameters
    ----------
    vhcl : VehicleObject
    vhclArray : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : AV is too close
        False : No AV is too close
    """
    safetyDistance = avProximityDistance
    vhclX = vhcl.getXYPosCntr()[0]
    vhclY = vhcl.getXYPosCntr()[1]

    for vhcls in vhclArray:
        vhclsX = vhcls.getXYPosCntr()[0]
        vhclsY = vhcls.getXYPosCntr()[1]

        carDst = math.sqrt(((vhclX - vhclsX)**2) + ((vhclY - vhclsY)**2) ) # Uses pythagorean theorum to find distance

        if carDst < safetyDistance:
            return True
    
    return False

def anyVhcls2Abreast(vhclArray):
    """
    SPC 2 Abreast Check

    Determines whether their are any vehicles traveling in parralel within the array

    Parameters
    ----------
    vhclArray : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : There ARE vehicles traveling in parralel in the array
        False : There AREN'T vehicles traveling in parralel in the array
    """
    responce = False
    for vhcl in vhclArray:
        if isVehicleToTheLeft(vhcl, vhclArray):
            responce = True
    return responce

def isVehicleToTheLeft(vhcl, vhclsWthnPrxmty):
    """
    Is there a vehicle to the left

    Checks whether there is a vehicle traveling to the left of the given vehicle

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsWthnPrxmty : array(VehicleObject)

    Returns
    -------
    Boolean
        True : IS vehicle to the left
        True : ISN'T vehicle to the left
    """
    relativeVhclsPstns = findRelativeCarPositionsSameDir(vhcl, vhclsWthnPrxmty, 4)
    if 1 in relativeVhclsPstns:
        return True
    else:
        return False

def getVhclsInfrnt(overtakingVhcl, vhclsTrvlngSmeDr):
    """
    Gather vehicles infront

    Gathers all vehicles infront of the current vehcile and returns them in an array

    Parameters
    ----------
    overtakingVhcl : VehicleObject
    vhclsTrvlngSmeDr : array(VehicleObject)

    Returns
    -------
    array(VehicleObject)
        Contains all vehicles that are infront of the vehicle
    """

    # Removing vehicle from vehicle array to stop it comparing against itself
    for vhcls in vhclsTrvlngSmeDr: 
        if vhcls.getVehicleId() == overtakingVhcl.getVehicleId():
            vhclsTrvlngSmeDr.remove(vhcls)

    vhclsInfront = []
    vhclDir = overtakingVhcl.getDirection()

    vhclFrntX  = overtakingVhcl.getXYPosFrnt()[0]
    vhclFrntY  = overtakingVhcl.getXYPosFrnt()[1]

    for vhclBngOvr in vhclsTrvlngSmeDr:

        vhclBngOvrRearBumprX  = vhclBngOvr.getXYPosRear()[0]
        vhclBngOvrRearBumprY  = vhclBngOvr.getXYPosRear()[1]
            
        # Traveling UP
        if vhclDir == 0.0 and vhclFrntY < vhclBngOvrRearBumprY:
            vhclsInfront.append(vhclBngOvr)
        # Traveling RIGHT
        elif vhclDir == 90.0 and vhclFrntX < vhclBngOvrRearBumprX:
            vhclsInfront.append(vhclBngOvr)
        # Traveling DOWN
        elif vhclDir == 180.0 and vhclFrntY > vhclBngOvrRearBumprY:
            vhclsInfront.append(vhclBngOvr)
        # Traveling LEFT
        elif vhclDir == 270.0 and vhclFrntX > vhclBngOvrRearBumprX:
            vhclsInfront.append(vhclBngOvr)

    return vhclsInfront

def getVhclInfrnt(overtakingVhcl, vhclsTrvlngSmeDr):
    """
    Gather closest vehicle infront

    Will return the vehicles that is closest, and is infront of the specified vehcile from the array

    Parameters
    ----------
    overtakingVhcl : VehicleObject
    vhclsTrvlngSmeDr : array(VehicleObject)

    Returns
    -------
    VehicleObject
        The vehicle which is closest to, and is infront of the vehicle
    """

    # Removing vehicle from vehicle array to stop it comparing against itself
    for vhcls in vhclsTrvlngSmeDr:
        if vhcls.getVehicleId() == overtakingVhcl.getVehicleId():
            vhclsTrvlngSmeDr.remove(vhcls)

    vhclDir = overtakingVhcl.getDirection()

    oVhclFrntBumprX  = overtakingVhcl.getXYPosFrnt()[0]
    oVhclFrntBumprY  = overtakingVhcl.getXYPosFrnt()[1]

    clstVhcl = None
    clstDst = None

    for vhclBngOvr in vhclsTrvlngSmeDr:

        vhclBngOvrRearBumprX  = vhclBngOvr.getXYPosRear()[0]
        vhclBngOvrRearBumprY  = vhclBngOvr.getXYPosRear()[1]
            
        # Traveling UP
        if vhclDir == 0.0 and oVhclFrntBumprY < vhclBngOvrRearBumprY:
            carDst = math.sqrt( ((oVhclFrntBumprX - vhclBngOvrRearBumprX)**2) + ((oVhclFrntBumprY - vhclBngOvrRearBumprY)**2) )
            if clstVhcl is None and clstDst is None:
                clstVhcl = vhclBngOvr
                clstDst = carDst
            elif carDst < clstDst:
                clstVhcl = vhclBngOvr
                clstDst = carDst
                
        # Traveling RIGHT
        elif vhclDir == 90.0 and oVhclFrntBumprX < vhclBngOvrRearBumprX:
            carDst = math.sqrt( ((oVhclFrntBumprX - vhclBngOvrRearBumprX)**2) + ((oVhclFrntBumprY - vhclBngOvrRearBumprY)**2) )
            if clstVhcl is None and clstDst is None:
                clstVhcl = vhclBngOvr
                clstDst = carDst
            elif carDst < clstDst:
                # print("CHANGED")
                clstVhcl = vhclBngOvr
                clstDst = carDst

        # Traveling DOWN
        elif vhclDir == 180.0 and oVhclFrntBumprY > vhclBngOvrRearBumprY:
            carDst = math.sqrt( ((oVhclFrntBumprX - vhclBngOvrRearBumprX)**2) + ((oVhclFrntBumprY - vhclBngOvrRearBumprY)**2) )
            if clstVhcl is None and clstDst is None:
                clstVhcl = vhclBngOvr
                clstDst = carDst
            elif carDst < clstDst:
                clstVhcl = vhclBngOvr
                clstDst = carDst

        # Traveling LEFT
        elif vhclDir == 270.0 and oVhclFrntBumprX > vhclBngOvrRearBumprX:
            carDst = math.sqrt( ((oVhclFrntBumprX - vhclBngOvrRearBumprX)**2) + ((oVhclFrntBumprY - vhclBngOvrRearBumprY)**2) )
            if clstVhcl is None and clstDst is None:
                clstVhcl = vhclBngOvr
                clstDst = carDst
            elif carDst < clstDst:
                clstVhcl = vhclBngOvr
                clstDst = carDst

    return clstVhcl


def isVhclInfntAV(vhcl, vhclsTrvlngSmeDr):
    """
    Is vehicle infront an AV

    Gathers the vehicles infront the given vehicle, and determines whether the vehicles is an AV.

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsTrvlngSmeDr : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : IS an AV infront
        False : ISN'T an AV infront
    """
    vhclInfrnt = getVhclInfrnt(vhcl, vhclsTrvlngSmeDr)
    minimumProximity = minimumProximityForOvertaking
    
    if vhclInfrnt is None: # Sometimes there's no vehicle infront
        return False
    else:
        vehicleProximity = math.sqrt( ((vhcl.getXYPosCntr()[0] - vhclInfrnt.getXYPosCntr()[0])**2) +  ((vhcl.getXYPosCntr()[1] - vhclInfrnt.getXYPosCntr()[1])**2) )

        if vehicleProximity > minimumProximity:
            return False
        elif not isAnySPC(vhclInfrnt):
            return True
        else:
            return False

def isWithinJunctionProximity(vhcl, safeDistance, netPath):
    """
    Is vehicles near junction

    Determines whether a vehicle is within proximity of a junction.

    Parameters
    ----------
    vhcl : VehicleObject
    safeDistance: Int
    netPath : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    Boolean
        True  : IS within proximity of the junction
        False : ISN'T within proximity of the junction
    """
    
    laneId = vhcl.getLaneID()
    laneLength = tr.lane.getLength(laneId)
    vhclPstn = vhcl.getLanePosition()
    
    if isSpecialEdge(vhcl, netPath): # Some lanes are "special", and are unable to support vehicles
        return False

    if vhclPstn < safeDistance or vhclPstn > (laneLength - safeDistance):
        return True
    else:
        return False

def distanceOfOppositeJunction(vhcl, safeDistance, netPath):
    """
    Is vehicles near junction

    Determines whether a vehicle is within proximity of a junction.

    Parameters
    ----------
    vhcl : VehicleObject
    safeDistance: Int
    netPath : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    Boolean
        True  : IS within proximity of the junction
        False : ISN'T within proximity of the junction
    """
    laneId = tr.vehicle.getLaneID(vhcl.getVehicleId())
    laneLength = tr.lane.getLength(laneId)
    vhclPstn = tr.vehicle.getLanePosition(vhcl.getVehicleId())

    if isSpecialEdge(vhcl, netPath): # Some lanes are "special", and are unable to support vehicles
        return False
    
    if vhclPstn > (laneLength - safeDistance):
        return True
    else:
        return False

def carWithinProximity(vhcl, allVhcls, vhclPrxmty):
    """
    Gather vhcls in proximity, if there are any

    Determines whether another vehicles is within the said vehicles radius, and if so, adds it to an array.

    Parameters
    ----------
    vhcl : VehicleObject
    allVhcls : array(VehicleObject)
    vhclPrxmty : Int

    Returns
    -------
    Boolean
        True  : Cars in proximity
        False : NO Cars in proximity
    Array(VehicleObject)
        Contains all vehicles within the given proximity
    """

    responce = False
    vhclsWthnPrxmty = []

    vhclxC = vhcl.getXYPosCntr()[0]
    vhclyC = vhcl.getXYPosCntr()[1]

    # Stops car from intercepting with itself
    for vhcls in allVhcls:
        if vhcls.getVehicleId() == vhcl.getVehicleId():
            allVhcls.remove(vhcls)

    for AV in allVhcls:
        AVxC = AV.getXYPosCntr()[0]
        AVyC = AV.getXYPosCntr()[1]

        distanceBetweenCars = math.sqrt(((AVxC - vhclxC)**2) + ((AVyC - vhclyC)**2))

        if distanceBetweenCars <= vhclPrxmty: # Cars Intersect
            responce = True
            vhclsWthnPrxmty.append(AV)

    return (responce, vhclsWthnPrxmty)

def areVhclsTrvlngOppstDir(vhcl, vhclsInPrxmty):
    """
    Are there cars traveling in the opposite direction

    Goes through an array of vehicles and determines whether any are traveling in the opposite direction.

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsInPrxmty : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : IS a vehicle traveling in the opposite direction
        False : ISNT a vehicle traveling in the opposite direction
    """
    responce = False

    for AV in vhclsInPrxmty:
        if int(vhcl.getDirection()) is int(((AV.getDirection() + 180.0)%360.0)):
            responce = True

    return responce

def getVhclsTrvlngOppstDir(vhcl, vhclsInPrxmty):
    """
    Gather Vehicles traveling in opposite direction

    Finds all vehicles traveling in the opposite direction, adds them to an array and returns the array

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsInPrxmty : array(VehicleObject)

    Returns
    -------
    array(VehicleObject)
        All vehicles that are traveling in the opposite direction
    """

    vhclsOpstDrctn = []

    for AV in vhclsInPrxmty:
        if int(vhcl.getDirection()) is int(((AV.getDirection() + 180.0)%360.0)):
            vhclsOpstDrctn.append(AV)

    return vhclsOpstDrctn

def canVhclRtrnToLane(vhclMain, allVhcls, netPath):

    """
    Move to Overtaking Lane

    Determines whether it is safe to overtake, and whether the 
    vehicles should overtake, and if so forces the vehicle to overtake

    Parameters
    ----------
    vhclMain : VehicleObject
    allVhcls : array(VehicleObject)
    netPath  : String
        String with path to the .net.xml file used in the simulations

    Returns
    -------
    Boolean
        True  : Vehicle did return
        False : Vehicle did NOT return 
    """

    # Making sure all updated vehicles are present
    allVhcls = []
    vhclIds = tr.vehicle.getIDList()

    for vhclId in vhclIds:
        vhcl = VehicleObj(vhclId)
        allVhcls.append(vhcl)

    for vhcls in allVhcls:
        if vhcls.getVehicleId() == vhclMain.getVehicleId():
            allVhcls.remove(vhcls)

    # Gathering whether there are vehicles are in proximity, and collecting cars within proximity into an array
    carPrxmtyTest = carWithinProximity(vhclMain, allVhcls, returningToLaneSafeDistance)
    isCarInPrxmty = carPrxmtyTest[0]
    carsWithinProximity = carPrxmtyTest[1]

    if not isWithinJunctionProximity(vhclMain, junctionProximitySafetyDistance, netPath): # If vehicle too close to junction, it would be unsafe to return

        if isCarInPrxmty:

            areVhclsTrvlngOppstDr = areVhclsTrvlngOppstDir(vhclMain, carsWithinProximity)
            vhclsTrvlngOppstDr = getVhclsTrvlngOppstDir(vhclMain, carsWithinProximity)

            # If vehicles are on the opposite side
            # A check must be made to - see wether there's SPC's, and if they can be turned into SPCO's
            # A check must be made to - see wether the SPCO had collided with another vehicle
            if areVhclsTrvlngOppstDr:
                if anySPC(vhclsTrvlngOppstDr):
                        if anyVhcls2Abreast(vhclsTrvlngOppstDr): # If vehicles are 2 abreast they will collide when changing lane
                            return False
                        else:
                            for SPC in vhclsTrvlngOppstDr:
                                moveToOvertakingLane(SPC, netPath)
                            return True

                if hasCarColided(vhclMain, vhclsTrvlngOppstDr): # Native vehicle collision won't work, custom must be used
                    print("FATAL ERROR: SPCO has collided with oncoming traffic")
                    return False

            # Gather vehicles traveling the same direction for checks
            areVhclsTrvlngSameDr = areVhclsTrvlngSameDir(vhclMain, carsWithinProximity)
            vhclsTrvlngSameDr = getVhclsTrvlngSameDir(vhclMain, carsWithinProximity)            
            
            if areVhclsTrvlngSameDr:
            
                avTrvlingSameDr = getAVhclsNoSPC(vhclsTrvlngSameDr)
                rltvVhclsPstnsSmeSide = findRelativeCarPositionsSameDir(vhclMain, vhclsTrvlngSameDr, 0)
                relativeVhclsPstnsAV = []

                if len(avTrvlingSameDr) > 0:
                    relativeVhclsPstnsAV = findRelativeCarPositionsSameDir(vhclMain, avTrvlingSameDr, 0)

                if (0 not in rltvVhclsPstnsSmeSide) and (-1 not in rltvVhclsPstnsSmeSide): # No vehicles within UNSAFE TO RETURN distance, nor to the RIGHT
                    if len(avTrvlingSameDr) > 0: 
                        if 2 not in relativeVhclsPstnsAV: # If Sucessfully past an AV - return to lane
                            moveToNonOvertakingLane(vhclMain, netPath)
                        else:
                            return False
                    else:
                        moveToNonOvertakingLane(vhclMain, netPath)
                        return True
            else:
                return False
        else:

            areVhclsTrvlngOppstDr = areVhclsTrvlngOppstDir(vhclMain, carsWithinProximity)

            if areVhclsTrvlngOppstDr: # Adjust vehicles in range proximity
                carPrxmtyTest = carWithinProximity(vhclMain, allVhcls, safeOvertakingDistance)
                isCarInPrxmty = carPrxmtyTest[0]

                if not isCarInPrxmty:
                    moveToNonOvertakingLane(vhclMain, netPath)
                    return True
                else:
                    return False
            else:
                moveToNonOvertakingLane(vhclMain, netPath)
    else:
        print("ERROR: Car too close to junction to return to lane")
        return False

    print("WARNING: FAILSAFE USED returning to lane")
    return False

def hasCarColided(vhcl, vhcls):
    """
    Has car collided

    Due to the inbuilt collision system being inaplicable, this function is used.
    It detects wether a car is parralel, and uses that information to detect a collision.

    Parameters
    ----------
    vhcl : VehicleObject
    vhcls : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : Car HAS collided
        False : Car has NOT collided
    """

    vhclsTrvlngOppstDr = getVhclsTrvlngOppstDir(vhcl, vhcls)
    avTrvlingOppstDr = getAVhclsNoSPC(vhclsTrvlngOppstDr)

    positions = findRelativeCarPositionsSameDir(vhcl, avTrvlingOppstDr, 1)

    if (0 in positions) or (1 in positions): # 0 - car to the left, 1 - car to the right
        return True
    else:
        return False

    return False

def areVhclsTrvlngSameDir(vhcl, vhclsInPrxmty):
    """
    Are there cars traveling in the same direction

    Goes through an array of vehicles and determines whether any are traveling in the same direction.

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsInPrxmty : array(VehicleObject)

    Returns
    -------
    Boolean
        True  : IS a vehicle traveling in the same direction
        False : ISNT a vehicle traveling in the sames direction
    """
    responce = False

    for AV in vhclsInPrxmty:
        if vhcl.getDirection() == AV.getDirection():
            responce = True

    return responce

def getVhclsTrvlngSameDir(vhcl, vhclsInPrxmty):
    """
    Gather Vehicles traveling in same direction

    Finds all vehicles traveling in the same direction, adds them to an array and returns the array

    Parameters
    ----------
    vhcl : VehicleObject
    vhclsInPrxmty : array(VehicleObject)

    Returns
    -------
    array(VehicleObject)
        All vehicles that are traveling in the same direction
    """

    vhclsSameDrctn = []

    for AV in vhclsInPrxmty:
        if int(vhcl.getDirection()) == int(AV.getDirection()):
            vhclsSameDrctn.append(AV)

    return vhclsSameDrctn

def findRelativeCarPositionsSameDir(vhclMain, allVhcls, safeDistance):
    """
    Find all vehicles relative position to vehicle

    By referencing the front, mid and rear of the vehicle we can determine whether another car is:
        -2 - Safely infront
        -1 - Unsafely infront
        0  - Right of vehicle
        1  - Left of vehicle
        2  - Behind vehicle

    Parameters
    ----------
    vhclMain : VehicleObject
    allVhcls : array(VehicleObject)
    safeDistance: Int

    Returns
    -------
    Array(Int)
        Array of values correlating to the relative vehicle positions
    """

    safeDistance = 5

    for vhcls in allVhcls:
        if vhcls.getVehicleId() == vhclMain.getVehicleId():
            allVhcls.remove(vhcls)        

    allResults = []

    vhclDir = vhclMain.getDirection()

    vhclFrntX = vhclMain.getXYPosFrnt()[0]
    vhclFrntY = vhclMain.getXYPosFrnt()[1]
    vhclRearX = vhclMain.getXYPosRear()[0]
    vhclRearY = vhclMain.getXYPosRear()[1]

    for rltvVhcl in allVhcls:

        rltvVhclDir = rltvVhcl.getDirection()

        rltvVhclFrntX = rltvVhcl.getXYPosFrnt()[0]
        rltvVhclFrntY = rltvVhcl.getXYPosFrnt()[1]
        rltvVhclRearX = rltvVhcl.getXYPosRear()[0]
        rltvVhclRearY = rltvVhcl.getXYPosRear()[1]

        # Traveling UP
        if vhclDir == 0.0 and vhclDir == rltvVhclDir:
            if vhclRearY > rltvVhclFrntY + safeDistance: # Vhcl has OVERTAKEN the relativeVhcl
                allResults.append(-2)
                break
            if vhclRearY > rltvVhclFrntY: # Vhcl has OVERTAKEN the relativeVhcl, but not safely ahead
                allResults.append(-1)
                break
            elif (vhclRearY <= rltvVhclFrntY and vhclRearY > rltvVhclRearY) or (vhclFrntY >= rltvVhclRearY and vhclFrntY < rltvVhclFrntY): # Vhcl is PARALLEL the relativeVhcl
                if rltvVhclFrntX > vhclFrntX: # Vehicle is to the RIGHT
                    allResults.append(0)
                    break
                if rltvVhclFrntX < vhclFrntX: # Vehicle is to the LEFT
                    allResults.append(1)
                    break
            elif vhclFrntY < rltvVhclRearY: # Vhcl is BEHIND the relativeVhcl
                allResults.append(2)
                break
            else:
                print("WARNING: Unexpected relative car detection system behaviour [0]")

        # Traveling RIGHT
        elif vhclDir == 90.0 and vhclDir == rltvVhclDir:
            if vhclRearX > rltvVhclFrntX + safeDistance: # Vhcl has OVERTAKEN the relativeVhcl
                allResults.append(-2)
            elif vhclRearX > rltvVhclFrntX: # Vhcl has OVERTAKEN the relativeVhcl, but not safely ahead
                allResults.append(-1)
            elif (vhclRearX <= rltvVhclFrntX and vhclRearX > rltvVhclRearX) or (vhclFrntX >= rltvVhclRearX and vhclFrntX < rltvVhclFrntX): # Vhcl is PARALLEL the relativeVhcl
                if rltvVhclFrntY < vhclFrntY: # Vehicle is to the RIGHT
                    allResults.append(0)
                if rltvVhclFrntY > vhclFrntY: # Vehicle is to the LEFT
                    allResults.append(1)
            elif vhclFrntX < rltvVhclRearX: # Vhcl is BEHIND the relativeVhcl
                allResults.append(2)
            else:
                print("WARNING: Unexpected relative car detection system behaviour [1]")

        # Traveling DOWN
        elif vhclDir == 180.0 and vhclDir == rltvVhclDir:
            if vhclRearY < rltvVhclFrntY - safeDistance: # Vhcl has OVERTAKEN the relativeVhcl
                allResults.append(-2)
            elif vhclRearY < rltvVhclFrntY: # Vhcl has OVERTAKEN the relativeVhcl, but not safely ahead
                allResults.append(-1)
            elif (vhclRearY >= rltvVhclFrntY and vhclRearY < rltvVhclRearY) or (vhclFrntY <= rltvVhclRearY and vhclFrntY > rltvVhclFrntY): # Vhcl is PARALLEL the relativeVhcl
                if rltvVhclFrntX < vhclFrntX: # Vehicle is to the RIGHT
                    allResults.append(0)
                if rltvVhclFrntX > vhclFrntX: # Vehicle is to the LEFT
                    allResults.append(1)
            elif vhclFrntY > rltvVhclRearY: # Vhcl is BEHIND the relativeVhcl
                allResults.append(2)
            else:
                print("WARNING: Unexpected relative car detection system behaviour [2]")

        # Traveling LEFT
        elif vhclDir == 270.0 and vhclDir == rltvVhclDir:
            if vhclRearX < rltvVhclFrntX - safeDistance: # Vhcl has OVERTAKEN the relativeVhcl
                allResults.append(-2)
            elif vhclRearX < rltvVhclFrntX: # Vhcl has OVERTAKEN the relativeVhcl, but not safely ahead
                allResults.append(-1)
            elif (vhclRearX >= rltvVhclFrntX and vhclRearX < rltvVhclRearX) or (vhclFrntX <= rltvVhclRearX and vhclFrntX > rltvVhclFrntX): # Vhcl is PARALLEL the relativeVhcl
                if rltvVhclFrntY > vhclFrntY: # Vehicle is to the RIGHT
                    allResults.append(0)
                if rltvVhclFrntY < vhclFrntY: # Vehicle is to the LEFT
                    allResults.append(1)
            elif vhclFrntX > rltvVhclRearX: # Vhcl is BEHIND the relativeVhcl
                allResults.append(2)
            else:
                print("WARNING: Unexpected relative car detection system behaviour [3]")

        elif not vhclDir == rltvVhclDir:
            print("Vehicles not traveling in the same direction")
    
    print('[%s]' % ', '.join(map(str, allResults)))
    return allResults