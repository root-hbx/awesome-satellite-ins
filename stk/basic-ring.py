from agi.stk12.stkdesktop import STKDesktop
from agi.stk12.stkobjects import *
from agi.stk12.stkutil import *
from agi.stk12.vgt import *
import os

# By Tasklist (on windows), u need to customize PID!!!
# -------------------------------
STK_PID = 764
# -------------------------------

stk = STKDesktop.AttachToApplication(pid=int(STK_PID))
root = stk.Root
print(type(root))

if root.CurrentScenario is not None:
    root.CloseScenario()

root.NewScenario("NewScenario")

print("===================new=======================")

scenario = root.CurrentScenario # link: current scenario
root.Rewind() # reset

# Add: GS
target = AgTarget(scenario.Children.New(AgESTKObjectType.eTarget,"GroundTarget"))
target.Position.AssignGeodetic(50,-100,0)

# Add: Satellite
satellite = AgSatellite(root.CurrentScenario.Children.New(AgESTKObjectType.eSatellite,"LeoSat"))
print(scenario.StartTime)
print(scenario.StopTime)
root.ExecuteCommand('SetState */Satellite/LeoSat Classical TwoBody "' + 
                    str(scenario.StartTime) + '" "' + str(scenario.StopTime) + 
                    '" 60 ICRF "' + str(scenario.StartTime) + '" 7200000.0 0.0 90 0.0 0.0 0.0');

print("Now we are good!")
