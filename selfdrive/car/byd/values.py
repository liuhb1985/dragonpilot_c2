from strenum import StrEnum
from typing import Dict, List, Union
from cereal import car
from pathlib import Path
from openpilot.selfdrive.car import AngleRateLimit, dbc_dict
from openpilot.selfdrive.car.docs_definitions import CarInfo
from dataclasses import dataclass

Ecu = car.CarParams.Ecu

# 日志路径定义
BYD_LOG_PATH = '/data/media/0/c2_logs/byd_logs/'
Path(BYD_LOG_PATH).mkdir(parents=True, exist_ok=True)

# 定义CAN总线
@dataclass
class CANBusMap:
  main: int = 0  # 主CAN
  radar: int = 1  # 毫米波雷达CAN
  camera: int = 2  # 摄像头CAN

CANBUS = CANBusMap()

# 比亚迪车型定义
class CAR(StrEnum):
  BYD_HAN_DM_20 = "BYD HAN DM 2020"
  BYD_HAN_EV_20 = "BYD HAN EV 2020"

# DBC文件映射
DBC = {
  CAR.BYD_HAN_DM_20: dbc_dict('byd_han_dmev_2020', None),
  CAR.BYD_HAN_EV_20: dbc_dict('byd_han_dmev_2020', None),
}

# 按钮状态定义
BUTTON_STATES = {
  'SET': 0x1,
  'RESUME': 0x2,
  'CANCEL': 0x4
}

# 档位映射
GEAR_MAP = {
  'P': car.CarState.GearShifter.park,
  'R': car.CarState.GearShifter.reverse,
  'N': car.CarState.GearShifter.neutral,
  'D': car.CarState.GearShifter.drive
}

CAR_INFO: Dict[str, Union[CarInfo, List[CarInfo]]] = {
  CAR.BYD_HAN_DM_20: CarInfo("比亚迪 汉DM 2020", "四驱性能版", min_steer_speed=3.5),
  CAR.BYD_HAN_EV_20: CarInfo("比亚迪 汉EV 2020", "创世版 610KM四驱尊享型", min_steer_speed=2.5),
}

class BydCarInfo:
  CAR_INFO = {
    # 更新车辆参数 ▼
    CAR.BYD_HAN_DM_20: {
      'mass': 2050,
      'wheelbase': 2.92,
      'steerRatio': 16.74,
      'centerToFront': 2.92 * 0.44,
      'tireStiffnessFactor': 1.00
    },
  }
  # 新增类级别参数 ▼
  LAT_ANGLE_MODE = False
  LAT_TORQ_KP = 1.0
  LAT_TORQ_KI = 0.1
  ACCEL_MAX = 2.0    # 新平台最大加速度
  ACCEL_MIN = -3.5   # 新平台最大减速度
  JERK_LIMITS = {
    'UP': 0.1,
    'DOWN': 0.5,
    'BP': [4, 10, 20, 40, 80],
    'V': {
      'LOWER': [-2.0, -1.8, -1.4, -1.0, -0.4],
      'UPPER': [0.8, 0.7, 0.6, 0.3, 0.2],
    }
  }
    
  def __init__(self, CP):
    self.STEER_LIMIT_TIMER = 0.5  # 所有车型使用更灵敏的计时器
    self.ANGLE_RATE_LIMIT_UP = AngleRateLimit(speed_bp=[0., 5., 15.], angle_v=[5., 1.0, 0.3])
    self.ANGLE_RATE_LIMIT_DOWN = AngleRateLimit(speed_bp=[0., 5., 15.], angle_v=[5., 5.0, 0.8])
    
    # 新增安全配置参数
    self.STEER_MAX = 300         # 最大转向扭矩
    self.STEER_DELTA_UP = 10     # 转向扭矩增加步长
    self.STEER_DELTA_DOWN = 25   # 转向扭矩减小步长
    self.STEER_DRIVER_ALLOWANCE = 50   # 驾驶员转向干预阈值
    self.STEER_DRIVER_MULTIPLIER = 2   # 驾驶员转向力矩系数
    self.STEER_DRIVER_FACTOR = 1       # 驾驶员转向因子
