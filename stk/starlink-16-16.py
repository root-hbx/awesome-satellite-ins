import time
# Create a Progress Bar on Console
from tqdm import tqdm
# STK Related
from comtypes.gen import STKObjects, STKUtil, AgSTKVgtLib
# Object Related
from comtypes.client import CreateObject, GetActiveObject, GetEvents, CoGetObject, ShowEvents
# Comtypes Related
from ctypes import *
from comtypes import GUID
from comtypes import helpstring
from comtypes import COMMETHOD
from comtypes import dispid
from ctypes.wintypes import VARIANT_BOOL
from ctypes import HRESULT
from comtypes import BSTR
from comtypes.automation import VARIANT
from comtypes.automation import _midlSAFEARRAY
from comtypes import CoClass
from comtypes import IUnknown
from comtypes.automation import IDispatch
from comtypes import DISPMETHOD, DISPPROPERTY, helpstring

############################################################################
# Scenario Setup
############################################################################

startTime = time.time()
useSTKEngine = False
readScenario = False

if useSTKEngine:
    # For Linux
    # (1) launch STK Engine
    print('Launching to STK Engine (STK12.2) ...')
    stkApp = GetActiveObject('STK12.Application')
    # (2) Disable graphics (on linux)
    stkApp.NoGraphics = True
    # (3) Ready for a new scenario
    print('Making a new stkRoot ...')
    stkRoot = CreateObject('AgStkObjects12.AgStkObjectRoot')
else:
    # For Windows
    # (1) launch STK
    print('Launching to STK (STK12.2) ...')
    if not readScenario:
        # creating a new scenario
        uiApp = CreateObject('STK12.Application')
    else:
        # from an existing scenario
        uiApp = GetActiveObject('STK12.Application')
    uiApp.Visible = True # GUI
    uiApp.UserControl = True # Mouse and GUI Console
    # (2) Ready for a new scenario
    print('Making a new stkRoot ...')
    stkRoot = uiApp.Personality2

'''
When creating a new scenario, the following code is needed
# For Linux (no GUI, create a new one):
stkRoot = CreateObject('AgStkObjects12.AgStkObjectRoot')
# For Windows (has GUI, complete instance):
stkRoot = stkApp.Personality2
'''

############################################################################
# Scenario Init
############################################################################

stkRoot.UnitPreferences.SetCurrentUnit('DateFormat', 'UTCG')
# Create a new scenario
print("Creating a new scenario ...")
if not readScenario:
    stkRoot.NewScenario('StarLink')

# eScenario Obj
scenario = stkRoot.CurrentScenario # python obj
print(scenario)
# IAgScenario Obj
scenario2 = scenario.QueryInterface(STKObjects.IAgScenario) # COM obj
print(scenario)

timeDuration = time.time() - startTime
splitTime = time.time()

print("--- Scenario creation: {a:4.3f} "
    "sec\t\tTotal time: {b:4.3f} sec ---".format(a=timeDuration, b=timeDuration))

'''
eScenario and IAgScenario:

- eScenario is a Python obj (object)
- IAgScenario is a COM obj (interface)

!!! You can only use IAgScenario to access STK Objects !!!
'''

############################################################################
# Constellation Setup
############################################################################

def CreateSatellite(
    numOrbitPlane=16, 
    numSatPerPlane=16, 
    hight=550, 
    inc=53,
    name="sat"
):
    # Create constellation object
    # eConstellation Obj
    constellation = scenario.Children.New(STKObjects.eConstellation, name)
    # IAgConstellation Obj
    constellation2 = constellation.QueryInterface(STKObjects.IAgConstellation)

    # Insert sat on each orbit plane
    for orbitIdx in range(numOrbitPlane):
        for satIdx in range(numSatPerPlane):
            # (1) Init a new satellite
            # eSatellite Obj
            satellite = scenario.Children.New(STKObjects.eSatellite, 
                                            f"{name}{orbitIdx}-{satIdx}")
            # IAgSatellite Obj
            satellite2 = satellite.QueryInterface(STKObjects.IAgSatellite)

            # (2) Two-body Propagator: IAgSatellite -> eSatellite
            satellite2.SetPropagatorType(STKObjects.ePropagatorTwoBody)
            twoBodyPropagator = satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)

            # (3) Init state
            keplarian = twoBodyPropagator.InitialState.Representation.ConvertTo(
                STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)
            # a:
            keplarian.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
            # h:
            keplarian.SizeShape.QueryInterface(
                STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = hight + 6371
            # e:
            keplarian.SizeShape.QueryInterface(
                STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = 0
            # inclination:
            keplarian.Orientation.Inclination = int(inc)
            # Arg of Perigee (近地点):
            keplarian.Orientation.ArgOfPerigee = 0
            # 升交点:
            keplarian.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
            # 使卫星均匀分布在不同轨道面上
            RAAN = 360 / numOrbitPlane * orbitIdx
            keplarian.Orientation.AscNode.QueryInterface(
                STKObjects.IAgOrientationAscNodeRAAN).Value = RAAN
            # 真近点角:
            keplarian.LocationType = STKObjects.eLocationTrueAnomaly
            # 使卫星在同一轨道面上均匀分布
            trueAnomaly = 360 / numSatPerPlane * satIdx
            keplarian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = trueAnomaly

            # (4) Propagate
            # All args -> keplarian -> twoBodyPropagator
            twoBodyPropagator.InitialState.Representation.Assign(keplarian)
            # Now do it
            twoBodyPropagator.Propagate()

            # (5) Add to constellation
            constellation2.Objects.AddObject(satellite)

############################################################################
# Sender and Receiver for Each Satellite
############################################################################

# Add Sender and Receiver for each Satellite
def AddTransmitterReceiver(sat_list):
    for each in sat_list:
        name = each.InstanceName
        # new transmitter and receiver
        transmitter = each.Children.New(STKObjects.eTransmitter, "Transmitter_" + name)
        reciver = each.Children.New(STKObjects.eReceiver, "Reciver_" + name)

# Sender Args
def SetTransmitterParameter(
    transmitter,
    frequency=12, 
    EIRP=20, 
    DataRate=14
):
    # 建立发射机的映射，以便对其进行设置
    transmitter2 = transmitter.QueryInterface(STKObjects.IAgTransmitter)
    # 选择 简单发射机 模型
    transmitter2.SetModel('Simple Transmitter Model')
    # Get Sending Model
    txModel = transmitter2.Model # py obj
    txModel = txModel.QueryInterface(STKObjects.IAgTransmitterModelSimple) # COM obj
    # Args
    txModel.Frequency = frequency
    txModel.EIRP = EIRP
    txModel.DataRate = DataRate

# Receiver Args
def SetReceiverParameter(receiver, GT=20, frequency=12):
    # 建立接收机的映射，以便对其进行设置
    receiver2 = receiver.QueryInterface(STKObjects.IAgReceiver)
    # 选择 简单接收机 模型
    receiver2.SetModel('Simple Receiver Model')
    # Get Sending Model
    recModel = receiver2.Model # py obj
    recModel = recModel.QueryInterface(STKObjects.IAgReceiverModelSimple) # COM obj
    # Args
    recModel.AutoTrackFrequency = False
    recModel.Frequency = frequency
    recModel.GOverT = GT
    return receiver2

# Get Receiver Instances
def GetSatReceiver(sat, GT=20, frequency=12):
    # py obj
    receiver = sat.Children.GetElements(STKObjects.eReceiver)[0]
    # COM obj
    receiver2 = SetReceiverParameter(receiver=receiver, GT=GT, frequency=frequency)

    return receiver2

############################################################################
# Compute Access (link-level)
############################################################################

def LinkComputeAccess(access):
    # Init for Access
    access.ComputeAccess()
    # Get DataProvider
    accessDP = access.DataProviders.Item('Link Information')
    accessDP2 = accessDP.QueryInterface(STKObjects.IAgDataPrvTimeVar)

    Elements = ["Time", 'Link Name', 'EIRP', 'Prop Loss', 'Rcvr Gain', "Xmtr Gain", "Eb/No", "BER"]
    results = accessDP2.ExecElements(scenario2.StartTime, scenario2.StopTime, 3600, Elements)

    Times = results.DataSets.GetDataSetByName('Time').GetValues()
    EbNo = results.DataSets.GetDataSetByName('Eb/No').GetValues()
    BER = results.DataSets.GetDataSetByName('BER').GetValues()
    Link_Name = results.DataSets.GetDataSetByName('Link Name').GetValues()
    Prop_Loss = results.DataSets.GetDataSetByName('Prop Loss').GetValues()
    Xmtr_Gain = results.DataSets.GetDataSetByName('Xmtr Gain').GetValues()
    EIRP = results.DataSets.GetDataSetByName('EIRP').GetValues()

    return Times, Link_Name, BER, EbNo, Prop_Loss, Xmtr_Gain, EIRP

# Get all Access
accessList = scenario2.GetExistingAccesses()
for accessPath in tqdm(accessList):
    # accessPath: ('Satellite/Sat0_0/Transmitter/Transmitter_Sat0_0','Satellite/Sat0_1/Receiver/Reciver_Sat0_1',True)
    # accessPath[0]: sender address
    # accessPath[1]: receiver address
    transmitterName = accessPath[0].split('/')[-1]
    reciverName = accessPath[1].split('/')[-1]
    access = scenario2.GetAccessBetweenObjectsByPath(accessPath[0], accessPath[1])
    link = access
    transmitterName = accessPath[0].split('/')[-1]
    reciverName = accessPath[1].split('/')[-1]
    access = scenario2.GetAccessBetweenObjectsByPath(accessPath[0], accessPath[1])

############################################################################
# Color the Satellite
############################################################################

def Change_Sat_color(sat_list):
    print('Changing Color of Satellite ...')

    for each_sat in tqdm(sat_list):
        now_sat_name = each_sat.InstanceName
        now_plane_num = int(now_sat_name.split('_')[0][3:])
        now_sat_num = int(now_sat_name.split('_')[1])

        satellite = each_sat.QueryInterface(STKObjects.IAgSatellite)
        graphics = satellite.Graphics
        graphics.SetAttributesType(1)  # eAttributesBasic
        attributes = graphics.Attributes
        attributes_color = attributes.QueryInterface(STKObjects.IAgVeGfxAttributesBasic)
        attributes_color.Inherit = False

        color_sheet = [16436871, 2330219, 42495, 9234160, 65535, 255, 16776960]
        if now_sat_name[2] == 'A':
            color = 255
        elif now_sat_name[2] == 'B':
            color = 42495
        elif now_sat_name[2] == 'C':
            color = 16436871
        attributes_color.Color = color
        # orbit attribute interface
        orbit = attributes.QueryInterface(STKObjects.IAgVeGfxAttributesOrbit)
        orbit.IsOrbitVisible = False

############################################################################
# Main
############################################################################

if not readScenario:
    CreateSatellite(numOrbitPlane=16, numSatPerPlane=16, hight=550, inc=53)
    sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    AddTransmitterReceiver(sat_list)

    # Change DateFormat dimension to epoch seconds to make the data easier to handle in
    # Python
    stkRoot.UnitPreferences.Item('DateFormat').SetCurrentUnit('EpSec')
    # Get the current scenario
    scenario = stkRoot.CurrentScenario
    # Set up the access object
    access = constellation2.GetAccessToObject()
    access.ComputeAccess()
    # Get the Access AER Data Provider
    accessDP = access.DataProviders.Item('Access Data').Exec(scenario.StartTime, scenario.StopTime)

    accessStartTimes = accessDP.DataSets.GetDataSetByName('Start Time').GetValues
    accessStopTimes = accessDP.DataSets.GetDataSetByName('Stop Time').GetValues
