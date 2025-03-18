from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car.byd.values import DBC, GEAR_MAP, BUTTON_STATES, CAR, BYD_LOG_PATH
from openpilot.selfdrive.car.interfaces import CarStateBase
from opendbc.can.parser import CANParser
from opendbc.can.can_define import CANDefine
from openpilot.system.swaglog import cloudlog

class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.can_define = CANDefine(DBC[CP.carFingerprint]['body'])
    self.button_states = {btn: False for btn in BUTTON_STATES.keys()}
    
    cloudlog.info(f"BYD状态: 初始化车型 - {CP.carFingerprint}", log_dir=BYD_LOG_PATH)

    # BYD特有状态
    self.epb_status = 0  # 电子驻车状态
    self.battery_soc = 0  # 电池SOC

    # 新增状态变量 ▼
    self.steering_rate = 0  # 转向角速度
    self.acc_state = 0      # ACC状态机
    self.lead_distance = 0  # 前车距离
    self.has_lead = False    # 前车存在标志
    self.lkas_available = False  # LKAS可用状态
    self.eps_torque_motor = 0     # EPS电机实际扭矩
    # ▲

  def update(self, cp, cp_cam):
    ret = car.CarState.new_message()

    # 车速（来自VCU 0x101报文）
    if self.CP.carFingerprint in (CAR.BYD_HAN_EV_20, CAR.BYD_HAN_DM_20):
        ret.vEgoRaw = cp.vl["VCU_Integrated"]["Vehicle_Speed"] * CV.KPH_TO_MS
        self.eps_torque_motor = cp.vl["EPS_Status"]["Actual_Torque_New"]
        self.acc_state = cp_cam.vl["ACC_HUD_NEW"]["ACC_State_New"]
        cloudlog.debug(f"BYD状态: 新平台车速 - {ret.vEgoRaw:.1f}m/s", log_dir=BYD_LOG_PATH)
    else:
        ret.vEgoRaw = cp.vl["VCU_Status"]["Vehicle_Speed"] * CV.KPH_TO_MS
        cloudlog.debug(f"BYD状态: 旧平台车速 - {ret.vEgoRaw:.1f}m/s", log_dir=BYD_LOG_PATH)

    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = (ret.vEgoRaw < 0.1)

    # 加速踏板（0x121报文）
    ret.gas = cp.vl["Motor_Status"]["Accel_Pedal_Pos"] / 100.0
    ret.gasPressed = ret.gas > 0.01

    # 制动状态（0x122报文）
    ret.brake = cp.vl["Brake_Status"]["Brake_Pressure"] / 100.0
    ret.brakePressed = cp.vl["Brake_Status"]["Brake_Switch"] == 1

    # 方向盘状态（0x2A4和0x130报文）
    ret.steeringAngleDeg = cp.vl["EPS_Status"]["Steer_Angle"]
    ret.steeringTorque = cp.vl["Steering_Column"]["Driver_Stn_Tq"]
    ret.steeringPressed = abs(ret.steeringTorque) > 1.5  # 检测驾驶员干预

    # 档位状态（0x115报文）
    gear_state = self.can_define.dv["Gear_Status"]["Gear_Position"].get(cp.vl["Gear_Status"]["Gear_Position"], "P")
    ret.gearShifter = GEAR_MAP.get(gear_state, car.CarState.GearShifter.unknown)

    # 按钮状态（0x316报文）
    buttonEvents = []
    for btn, val in BUTTON_STATES.items():
      state = cp.vl["Steering_Button"][btn] == val
      if self.button_states[btn] != state:
        event = car.CarState.ButtonEvent.new_message()
        event.type = btn
        event.pressed = state
        buttonEvents.append(event)
      self.button_states[btn] = state
    ret.buttonEvents = buttonEvents

    # 电子驻车状态（0x305报文）
    self.epb_status = cp.vl["EPB_Status"]["EPB_State"]
    ret.epbFault = self.epb_status == 3  # 故障状态

    # 电池状态（0x108报文）
    self.battery_soc = cp.vl["BMS_Status"]["Batt_SOC"]

    # 车门状态（0x310报文）
    ret.doorOpen = any([cp.vl["Door_Status"]["Driver_Door"], 
                      cp.vl["Door_Status"]["Passenger_Door"],
                      cp.vl["Door_Status"]["Rear_Left_Door"],
                      cp.vl["Door_Status"]["Rear_Right_Door"]])

    # 安全带（0x311报文）
    ret.seatbeltUnlatched = cp.vl["Seatbelt_Status"]["Driver_Belt"] == 0

    # 转向故障检测
    eps_status = cp.vl["EPS_Status"]["EPS_Mode"]
    ret.steerFaultPermanent = eps_status not in [1, 2]
    if ret.steerFaultPermanent:
        cloudlog.warning(f"BYD状态: EPS故障 - 模式:{eps_status}", log_dir=BYD_LOG_PATH)

    # ACC状态监测
    self.acc_state = cp_cam.vl["ACC_HUD"]["ACC_State"]
    ret.cruiseState.speed = cp_cam.vl["ACC_HUD"]["Set_Speed"] * CV.KPH_TO_MS
    ret.cruiseState.enabled = self.acc_state in (3, 5)
    cloudlog.debug(f"BYD状态: ACC状态 - 状态:{self.acc_state} 目标速度:{ret.cruiseState.speed:.1f}m/s", log_dir=BYD_LOG_PATH)

    # 前车距离检测
    self.lead_distance = cp_cam.vl["ACC_HUD"]["Lead_Distance"]
    self.has_lead = cp_cam.vl["ACC_HUD"]["Lead_Exist"] == 1
    if self.has_lead:
        cloudlog.debug(f"BYD状态: 检测到前车 - 距离:{self.lead_distance:.1f}m", log_dir=BYD_LOG_PATH)

    # 新增LKAS状态检测 ▼
    self.lkas_available = cp.vl["EPS_Status"]["LKAS_Ready"] == 1
    self.eps_torque_motor = cp.vl["EPS_Status"]["Actual_Torque"]
    # ▲

    return ret

  @staticmethod
  def get_can_parser(CP):
    # 修复信号定义格式和车型引用 ▼
    signals = [
      ("Vehicle_Speed", "VCU_Integrated", 0),    # 信号名, 报文名, 起始字节
      ("Actual_Torque_New", "EPS_Status", 0),
      ("ACC_State_New", "ACC_HUD_NEW", 0),
    ] if CP.carFingerprint in (CAR.BYD_HAN_DM_20, CAR.BYD_HAN_EV_20) else []
    
    # 添加通用信号定义 ▼
    signals += [
      ("Vehicle_Speed", "VCU_Status", 0),
      ("Accel_Pedal_Pos", "Motor_Status", 0),
      ("Brake_Pressure", "Brake_Status", 0),
      ("Brake_Switch", "Brake_Status", 0),  # 添加制动开关信号
      ("Steer_Angle", "EPS_Status", 0),
      ("Gear_Position", "Gear_Status", 0),
      ("EPB_State", "EPB_Status", 0),
      ("Batt_SOC", "BMS_Status", 0),
      ("Driver_Stn_Tq", "Steering_Column", 0),
      ("EPS_Mode", "EPS_Status", 0),
      ("Steer_Angle_Rate", "EPS_Status", 0),
      ("LKAS_Ready", "EPS_Status", 0),
      ("Actual_Torque", "EPS_Status", 0),
      # 添加车门信号
      ("Driver_Door", "Door_Status", 0),
      ("Passenger_Door", "Door_Status", 0),
      ("Rear_Left_Door", "Door_Status", 0),
      ("Rear_Right_Door", "Door_Status", 0),
      # 添加安全带信号
      ("Driver_Belt", "Seatbelt_Status", 0),
      # 添加方向盘按钮信号
      ("SET", "Steering_Button", 0),
      ("RESUME", "Steering_Button", 0),
      ("CANCEL", "Steering_Button", 0),
    ]

    messages = [(msg, freq) for msg, freq in [
      ("VCU_Integrated", 50),      # 新平台集成车速
      ("VCU_Status", 50),
      ("Motor_Status", 100),
      ("Brake_Status", 50),
      ("EPS_Status", 50),
      ("Gear_Status", 10),
      ("Steering_Button", 10),
      ("EPB_Status", 5),
      ("BMS_Status", 5),
      ("Door_Status", 5),
      ("Seatbelt_Status", 5),
      ("Steering_Column", 50),
      ("ACC_HUD", 50),
      ("ACC_HUD_NEW", 50),         # 添加新平台ACC报文
    ]]

    checks = [(msg, freq) for msg, freq in [
      ("VCU_Status", 50),
      ("EPS_Status", 50),
      ("Motor_Status", 100),
    ]]
    
    return CANParser(DBC[CP.carFingerprint]['body'], signals, messages, checks)

  @staticmethod 
  def get_cam_can_parser(CP):
    signals = [
      ("ACC_State", "ACC_HUD", 0),
      ("Set_Speed", "ACC_HUD", 0),
      ("Lead_Distance", "ACC_HUD", 0),
      ("Lead_Exist", "ACC_HUD", 0),
    ]
    checks = [
      ("ACC_HUD", 50),
    ]
    return CANParser(DBC[CP.carFingerprint]['body'], signals, checks, 0)