###############################################################################
## Task 0: Const Def
###############################################################################

# --------------------------------------
# Scenrio
# --------------------------------------

ScName = 'Paper'
InitTm = '18 May 2022 09:21:00.000'
FinalTm = '3 Jun 2022 23:32:30.830'
StepTm = 8 # time step: 8s

# --------------------------------------
# GS and Receiver
# --------------------------------------

# Ground Station
CBA_GdStaName = 'CordBS'
CBA_GdStaLat = -31.4343 # Latitude (纬度)
CBA_GdStaLon = -64.2672 # longitude (经度)
CBA_GdStaAlt = 0 # altitude (海拔)
POLAR_GdStaName = 'polarBS'
POLAR_GdStaLat = -90
POLAR_GdStaLon = -90
POLAR_GdStaAlt = 0
# Receiver
CBA_RecName = 'Receiver2'
RecType = 'Simple Receiver Model'
POLAR_RecName = 'Receiver3'

# --------------------------------------
# Satellite and Sender
# --------------------------------------

# Sender
TraName = 'Transmitter2'
# Satellite
SaName = 'Saocom-1-B'

# --------------------------------------
# Physical Devices
# --------------------------------------

# Demodulation (解调)
DemOptions = ['QPSK', '8PSK', '16PSK', 'QAM16', 'QAM32']
Dem = DemOptions[0]

# Data Rare
DataRateOptions = [2, 3, 4, 4, 5]
DataRate = DataRateOptions[0]

# Antenna (天线)
XantPosition = 50
YantPosition = -100
ZantPosition = 0
ElvOptions = [-65, -32.5, 0, 32.5, 65]
Elv = ElvOptions[0]

###############################################################################
## Task 1: STK App/Engine Setup
###############################################################################

from win32api import GetSystemMetrics
from comtypes.client import CreateObject

# 1. Get reference to running STK instance
uiApplication = CreateObject('STK12.Application') # STK 12.2
uiApplication.Visible = True # GUI Demo
uiApplication.UsarControl = True # Mouse Interaction

# 2. Get IAgStkObjectRoot interface
root = uiApplication.Personality2

'''
When 'root=uiApplication.Personality2' is executed, 
the comtypes library automatically creates a gen folder that contains STKUtil and STK Objects.

After running this at least once on your computer, the following two lines should be moved before 
the 'uiApplication=CreateObject("STK12.Application")' line for improved performance.
'''
from comtypes.gen import STKObjects
from comtypes.gen import STKUtil

###############################################################################
## Task 2: Scenario Setup
###############################################################################

# 1. Init a new scenario
root.NewScenario(ScName)
scenarioSTKObj = root.CurrentScenario
# 2. Set the analytical time period
scenarioScObj = scenarioSTKObj.QueryInterface(STKObjects.IAgScenario) # COM Obj
scenarioScObj.SetTimePeriod(InitTm, FinalTm)
scenarioScObj.Animation.AnimStepValue = StepTm
## 3. Reset the animation time
root.Rewind()

###############################################################################
## Task 3: Add Two GS
###############################################################################

# CORDOBA'S GROUND STATION
CBAGdSta_STKObj = root.CurrentScenario.Children.New(8, CBA_GdStaName)
CBAGdSta_FaObj = CBAGdSta_STKObj.QueryInterface(STKObjects.IAgFacility)
root.UnitPreferences.Item('LatitudeUnit').SetCurrentUnit('deg')
root.UnitPreferences.Item('LongitudeUnit').SetCurrentUnit('deg')
CBAGdSta_FaObj.UseTerrain = False
CBAGdSta_FaObj.Position.AssignGeodetic(CBA_GdStaLat, CBA_GdStaLon, CBA_GdStaAlt)

# POLAR'S GROUND STATION
POLARGdSta_STKObj = root.CurrentScenario.Children.New(8, POLAR_GdStaName)
POLARGdSta_FaObj = POLARGdSta_STKObj.QueryInterface(STKObjects.IAgFacility)
root.UnitPreferences.Item('LatitudeUnit').SetCurrentUnit('deg')
root.UnitPreferences.Item('LongitudeUnit').SetCurrentUnit('deg')
POLARGdSta_FaObj.UseTerrain = True
POLARGdSta_FaObj.Position.AssignGeodetic(POLAR_GdStaLat, POLAR_GdStaLon, POLAR_GdStaAlt)

###############################################################################
## Task 4: Add Receiver to GS
###############################################################################

# -----------------------------------------------------------------------------
# 1. Init Receiver Obj (COM)
# -----------------------------------------------------------------------------

# CORDOBA'S RECEPTOR
CBArec_STKObj = CBAGdSta_STKObj.Children.New(17, CBA_RecName)  # py Obj
CBArec_RecObj = CBArec_STKObj.QueryInterface(STKObjects.IAgReceiver) # COM Obj
# POLAR'S RECEPTOR
POLARrec_STKObj = POLARGdSta_STKObj.Children.New(17, POLAR_RecName)  # py Obj
POLARrec_RecObj = POLARrec_STKObj.QueryInterface(STKObjects.IAgReceiver) #COM Obj

# -----------------------------------------------------------------------------
# 2. Modify Receiver Type
# -----------------------------------------------------------------------------

CBArec_RecObj.SetModel(RecType)  # CORDOBA
POLARrec_RecObj.SetModel(RecType)  # POLAR

# -----------------------------------------------------------------------------
# 3. Modify Receiver Demodulator Properties
# -----------------------------------------------------------------------------

# CORDOBA'S RECEPTOR
CBArecModel_ModObj = CBArec_RecObj.Model
CBArecModel_SModObj = CBArecModel_ModObj.QueryInterface(
    STKObjects.IAgReceiverModelSimple)
CBArecModel_SModObj.AutoSelectDemodulator = False
CBArecModel_SModObj.SetDemodulator(Dem)
CBArecModel_SModObj.GOverT = 24.83  # dB/K

# POLAR'S RECEPTOR
POLARrecModel_ModObj = POLARrec_RecObj.Model
POLARrecModel_SModObj = POLARrecModel_ModObj.QueryInterface(
    STKObjects.IAgReceiverModelSimple)
POLARrecModel_SModObj.AutoSelectDemodulator = False
POLARrecModel_SModObj.SetDemodulator(Dem)
POLARrecModel_SModObj.GOverT = 24.83  # dB/K

###############################################################################
## Task 5: Satellite and Sender Setup
###############################################################################

# -----------------------------------------------------------------------------
# 1. Add a Satellite object to the scenario
# -----------------------------------------------------------------------------

# Init a Sat Object
SAOCOMsa_STKObj = root.CurrentScenario.Children.New(18, SaName)  # py obj
SAOCOMsa_SaObj = SAOCOMsa_STKObj.QueryInterface(STKObjects.IAgSatellite) # COM obj
SAOCOMsa_SaObj.SetPropagatorType(STKObjects.ePropagatorSGP4)

# Set Sat Propagator to SGP4
CBAprop_PropObj = SAOCOMsa_SaObj.Propagator
CBAprop_SGP4Obj = CBAprop_PropObj.QueryInterface(STKObjects.IAgVePropagatorSGP4)
CBAprop_SGP4Obj.EphemerisInterval.SetImplicitInterval(
    root.CurrentScenario.Vgt.EventIntervals.Item("AnalysisInterval"))  # Link to scenario period
CBAprop_SGP4Obj.Step = StepTm
CBAprop_SGP4Obj.AutoUpdateEnabled = False

# Propagate
CBAprop_SGP4Obj.Propagate()

# Set satellite attitude basic spinning
CBAatt_AttObj = SAOCOMsa_SaObj.Attitude
CBAatt_OrbitAttStdObj = CBAatt_AttObj.QueryInterface(STKObjects.IAgVeOrbitAttitudeStandard)
CBAatt_BasicObj = CBAatt_OrbitAttStdObj.Basic
CBAatt_BasicObj.SetProfileType(6)
CBAatt_ProfObj = CBAatt_BasicObj.Profile
CBAatt_FIAObj = CBAatt_ProfObj.QueryInterface(STKObjects.IAgVeProfileFixedInAxes)
CBAatt_FIAObj.ReferenceAxes = 'Satellite/Saocom-1-B LVLH(Earth)'
CBAatt_OrintObj = CBAatt_FIAObj.Orientation
CBAatt_OrintObj.AssignYPRAngles(4, -180, 0, -90)

# -----------------------------------------------------------------------------
# 2. Init an antenna object and set properties
# -----------------------------------------------------------------------------

SAOCOMant_STKObj = SAOCOMsa_STKObj.Children.New(31, 'SAOCOMantenna')
SAOCOMant_AntObj = SAOCOMant_STKObj.QueryInterface(STKObjects.IAgAntenna)
SAOCOMant_AntObj.SetModel('Bessel Aperture Circular')
SAOCOMant_AntModObj = SAOCOMant_AntObj.Model
SAOCOMant_AntSABObj = SAOCOMant_AntModObj.QueryInterface(
    STKObjects.IAgAntennaModelApertureCircularBessel)
SAOCOMant_AntSABObj.Diameter = 0.5  # m
SAOCOMant_AntSABObj.ComputeMainlobeGain = False
SAOCOMant_AntModObj.DesignFrequency = 2.255  # GHz
SAOCOMant_OrintObj = SAOCOMant_AntObj.Orientation
SAOCOMant_OrintObj.AssignAzEl(0, Elv, 1)

# -----------------------------------------------------------------------------
# 3. Add a Transmitter object to the satellite
# -----------------------------------------------------------------------------

CBAtra_STKObj = SAOCOMsa_STKObj.Children.New(24, TraName)  # py Obj
CBAtra_TraObj = CBAtra_STKObj.QueryInterface(STKObjects.IAgTransmitter) # COM Obj

# Modify Transmitter Modulator Properties
CBAtra_TraObj.SetModel('Complex Transmitter Model')
CBAtxModel_ModObj = CBAtra_TraObj.Model
CBAtxModel_CmxModObj = CBAtxModel_ModObj.QueryInterface(STKObjects.IAgTransmitterModelComplex)
CBAtxModel_CmxModObj.SetModulator(Dem)
CBAtxModel_CmxModObj.Modulator.AutoScaleBandwidth = True
CBAtxModel_CmxModObj.Frequency = 2.255  # GHz
CBAtxModel_CmxModObj.Power = -14  # dBW
CBAtxModel_CmxModObj.DataRate = DataRate  # Mb/sec
CBAtxModel_CmxModObj.AntennaControl.ReferenceType = 0  # Link to an Antenna object

SAOCOMmass = SAOCOMsa_SaObj.MassProperties
SAOCOMmass.Mass = 0.00100000

print('The Configuration is Done. Please upload the TLE')


def report():
    for modulation in range(len(DemOptions)):
        for angle in range(len(ElvOptions)):
            single_report(DemOptions[modulation], ElvOptions[angle])
    print('Done')


def single_report(Demodulation, Angle):
    Dem = Demodulation
    Elv = Angle
    'QPSK', '8PSK', '16PSK', 'QAM16', 'QAM32'
    if Demodulation == 'QPSK':
        DataRate = DataRateOptions[0]
    elif Demodulation == '8PSK':
        DataRate = DataRateOptions[1]
    elif Demodulation == '16PSK':
        DataRate = DataRateOptions[2]
    elif Demodulation == 'QAM16':
        DataRate = DataRateOptions[3]
    elif Demodulation == 'QAM32':
        DataRate = DataRateOptions[4]
    
    CBArecModel_SModObj.SetDemodulator(Dem)
    POLARrecModel_SModObj.SetDemodulator(Dem)
    CBAtxModel_CmxModObj.DataRate = DataRate  # Mb/sec
    SAOCOMant_OrintObj.AssignAzEl(0, Elv, 1)
    CBAtxModel_CmxModObj.SetModulator(Dem)
    access = CBArec_STKObj.GetAccessToObject(CBAtra_STKObj)
    access.ComputeAccess()
    AccessData = access.DataProviders.Item('Access Data')
    AccessData_ProvG = AccessData.QueryInterface(STKObjects.IAgDataPrvInterval)
    AccessData_results = AccessData_ProvG.Exec(scenarioScObj.StartTime, scenarioScObj.StopTime)
    accessStartTime = AccessData_results.DataSets.GetDataSetByName('Start Time').GetValues()
    accessStopTime = AccessData_results.DataSets.GetDataSetByName('Stop Time').GetValues()
    
    print(accessStartTime, accessStopTime)

report()

'''
Usually:

- Transmitter is combined with Satellite
- Receiver is combined with GS
'''
