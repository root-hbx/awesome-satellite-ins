from comtypes.client import CreateObject
from comtypes.gen import STKObjects
# 创建STK12桌面应用
stk = CreateObject("STK12.Application")
# STK12可见
stk.Visible = 1
# 获取IAgStkObjectRoot接口
root = stk.Personality2
# 查看root属性
root.NewScenario('sce_test')
# 让变量Sce获取场景句柄
Sce = root.CurrentScenario

# 创建sat0，sat1...sat7 共8颗卫星
for num in range(0,8):  # 
    SatObj = Sce.Children.New(18,'sat'+str(num))
    SatIAF = SatObj.QueryInterface(STKObjects.IAgSatellite)
    #查看当前卫星轨道预报模型
    SatIAF.PropagatorType
    # 其返回值为7，表示预报模型为二体模型(ePropagatorTwoBody)
    ProIAF = SatIAF.Propagator
    # 由IAgVePropagator跳转至IAgVePropagatorTwoBody
    ProTwoBodyIAF = ProIAF.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
    # 设置卫星坐标系为J2000，轨道六要素为7000km，0，num×10°，0°，0°，0°
    ProTwoBodyIAF.InitialState.Representation.AssignClassical(3,7000,0,num*10,0,0,0)
    # 传递参数
    ProTwoBodyIAF.Propagate()

# 保存Scenario2.sc文件（路径DIY）
root.SaveAs(r'C:\testSTK\Scenario2.sc')
# 保存Scenario2.vdf文件
root.SaveAs(r'C:\testSTK\Scenario2.vdf')

print("Now we are good!")
