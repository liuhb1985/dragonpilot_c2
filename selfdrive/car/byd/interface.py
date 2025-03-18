#!/usr/bin/env python3
from cereal import car
from openpilot.selfdrive.car.byd.values import CAR, CarControllerParams, BYD_LOG_PATH
from openpilot.selfdrive.car import get_safety_config
from openpilot.selfdrive.car.interfaces import CarInterfaceBase
from openpilot.system.swaglog import cloudlog

class CarInterface(CarInterfaceBase):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.cruise_enabled_prev = False
    cloudlog.info(f"BYD接口: 初始化车型 - {self.CP.carFingerprint}", log_dir=BYD_LOG_PATH)

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "byd"
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.byd)]
    
    # 记录车辆配置信息
    cloudlog.info(f"BYD接口: 配置参数 - 车型:{candidate} BSM:{0x1048 in fingerprint[0]}", log_dir=BYD_LOG_PATH)

    # 新增通用配置 ▼
    ret.autoResumeSng = True
    ret.enableBsm = 0x1048 in fingerprint[0]
    ret.transmissionType = car.CarParams.TransmissionType.direct
    ret.minEnableSpeed = -1
    # ▲

    # 车型参数扩展 ▼
    # 更新车型判断条件
    if candidate in (CAR.BYD_HAN_DM_20, CAR.BYD_HAN_EV_20):
        ret.mass = 2020.
        ret.wheelbase = 2.92
        ret.centerToFront = ret.wheelbase * 0.4
        ret.steerRatio = 16.0
        ret.steerRateCost = 0.5
        ret.maxLateralAccel = 2.0
        cloudlog.info(f"BYD接口: 汉系列参数 - 轴距:{ret.wheelbase}m 转向比:{ret.steerRatio}", log_dir=BYD_LOG_PATH)
    # ▲

    # 横向控制模式切换 ▼
    if CarControllerParams.LAT_ANGLE_MODE:
        cloudlog.info("BYD接口: 使用角度控制模式", log_dir=BYD_LOG_PATH)
        ret.lateralTuning.init('pid')
        ret.lateralTuning.pid.kpBP = CarControllerParams.LATERAL_BP
        ret.lateralTuning.pid.kiBP = CarControllerParams.LATERAL_BP
        ret.lateralTuning.pid.kpV = CarControllerParams.LATERAL_KP
        ret.lateralTuning.pid.kiV = CarControllerParams.LATERAL_KI
    else:
        cloudlog.info("BYD接口: 使用力矩控制模式", log_dir=BYD_LOG_PATH)
        ret.lateralTuning.init('torque')
        ret.lateralTuning.torque.useSteeringAngle = True
        ret.lateralTuning.torque.kp = CarControllerParams.LAT_TORQ_KP
        ret.lateralTuning.torque.ki = CarControllerParams.LAT_TORQ_KI
    # ▲
    
    return ret

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)
    ret.events = self.create_common_events(ret).to_msg()
    
    # 记录重要状态变化
    if ret.cruiseState.enabled != self.cruise_enabled_prev:
        cloudlog.info(f"BYD接口: 巡航状态变化 - {ret.cruiseState.enabled}", log_dir=BYD_LOG_PATH)
    
    if ret.vEgo < self.CP.minSteerSpeed and ret.cruiseState.enabled:
        cloudlog.warning(f"BYD接口: 车速过低 - {ret.vEgo:.1f}m/s", log_dir=BYD_LOG_PATH)
    ret.cruiseState.standstill = self.CS.epb_status == 2  # 电子驻车触发保持
    
    # 修复事件处理位置 ▼
    if ret.cruiseState.enabled:
        if not self.cruise_enabled_prev:
            ret.events.add(car.CarEvent.EventName.pcmEnable)
        if ret.vEgo < self.CP.minSteerSpeed:
            ret.events.add(car.CarEvent.EventName.belowSteerSpeed)
    else:
        if self.cruise_enabled_prev:
            ret.events.add(car.CarEvent.EventName.pcmDisable)
    
    self.cruise_enabled_prev = ret.cruiseState.enabled
    # ▲
    
    return ret

  def apply(self, c, now_nanos):
    return self.CC.update(c, self.CS, now_nanos)
