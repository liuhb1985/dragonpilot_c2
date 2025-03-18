from openpilot.common.numpy_fast import clip, interp
from openpilot.common.params import Params
from openpilot.selfdrive.car import apply_driver_steer_torque_limits
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car.byd.values import DBC, CarControllerParams, CAR, BYD_LOG_PATH
from openpilot.system.swaglog import cloudlog

class CarController:
  def __init__(self, dbc_name, CP, VM):
    self.first_start = True
    self.steer_max_limit = 0
    self.CP = CP
    self.params = CarControllerParams(CP)
    self.frame = 0
    self.apply_steer_last = 0
    self.packer = CANPacker(DBC[CP.carFingerprint]['eps'])
    
    cloudlog.info(f"BYD控制: 初始化车型 - {CP.carFingerprint}", log_dir=BYD_LOG_PATH)
    
    # BYD特有参数
    self.steer_step = 0  # 转向控制步进计数器
    self.epb_status = 0  # 电子驻车状态
    
    self.mpc_counter = 0
    self.eps_counter = 0
    self.steer_rate_limited = False
    self.steer_rate_limit = 1.0
    self.steer_max_limit = 0
    self.lkas_active = False
    self.lat_safeoff = 0
    self.param_s = Params()

  def update(self, CC, CS, now_nanos):
    can_sends = []
    steer_angle_enabled = CC.latActive and CS.out.vEgo > self.CP.minSteerSpeed
    apply_steer = 0

    if self.frame % 2 == 0:
      if CC.latActive:
        if self.CP.carFingerprint in (CAR.BYD_HAN_DM_20, CAR.BYD_HAN_EV_20):
          if self.steer_max_limit < self.params.STEER_MAX:
            self.steer_max_limit += 6
            cloudlog.debug(f"BYD控制: 转向力矩渐入 - {self.steer_max_limit}", log_dir=BYD_LOG_PATH)

        new_steer = int(CC.actuators.steer * self.steer_max_limit) 
        apply_steer = apply_driver_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.params)
        
        if abs(apply_steer) > self.params.STEER_MAX * 0.9:
          cloudlog.warning(f"BYD控制: 转向力矩接近限制 - {apply_steer}", log_dir=BYD_LOG_PATH)

    # 纵向控制记录
    if self.frame % 5 == 0 and self.CP.openpilotLongitudinalControl:
      modified_stock = self.param_s.get_bool("dp_byd_modified_stock_long")
      lead_dist = CS.radarState.leadOne.dRel or 0
      
      if modified_stock:
        accel = self._modified_stock_accel(CC.actuators.accel, lead_dist)
        cloudlog.debug(f"BYD控制: 原厂风格加速度 - 请求:{CC.actuators.accel:.2f} 修正:{accel:.2f} 前车距离:{lead_dist:.1f}", 
                      log_dir=BYD_LOG_PATH)

    # 错误状态记录
    if CC.cruiseControl.cancel:
      cloudlog.info("BYD控制: 巡航取消请求", log_dir=BYD_LOG_PATH)

    # 增强纵向控制 ▼
    if self.frame % 5 == 0 and self.CP.openpilotLongitudinalControl:
      modified_stock = self.param_s.get_bool("dp_byd_modified_stock_long")
      lead_dist = CS.radarState.leadOne.dRel or 0
      
      if modified_stock:  # 新增原厂风格控制
        accel = self._modified_stock_accel(CC.actuators.accel, lead_dist)
      else:
        accel = clip(CC.actuators.accel, -1.0, 1.0)

    # 新增UI状态反馈 ▼
    if self.frame % 10 == 0:
      can_sends.append(self.packer.make_can_msg("LKAS_HUD", 0, {
        "LeftLaneState": CS.left_lane + 1,
        "RightLaneState": CS.right_lane + 1,
        "LKAS_AlarmType": CC.hudControl.visualAlert
      }))
    # ▲
      
      # 发送EPS控制报文（0x2A4）
      can_sends.append(self.packer.make_can_msg("EPS_Control", 0, {
        "Steer_Req": 1 if steer_angle_enabled else 0,
        "Steer_Tq_Req": apply_steer,  # 现在变量已正确初始化
        "Steer_Control_Counter": self.steer_step % 16,
      }))
      
      self.apply_steer_last = apply_steer
      self.steer_step += 1

    # 纵向控制（20Hz）
    if self.frame % 5 == 0 and self.CP.openpilotLongitudinalControl:
      # 加速控制（0x121）
      accel = clip(CC.actuators.accel, -1.0, 1.0)
      can_sends.append(self.packer.make_can_msg("VCU_Accel_Control", 0, {
        "Accel_Pedal_Pos": int(accel * 100),  # 百分比
        "ACC_Enable": 1 if CC.longActive else 0,
        "ACC_Counter": self.frame % 256,
      }))

      # 制动控制（0x122）
      can_sends.append(self.packer.make_can_msg("Brake_Control", 0, {
        "Brake_Pedal_Pos": int(abs(accel) * 100) if accel < 0 else 0,
        "Brake_Req_Active": 1 if accel < 0 else 0,
      }))

    # 电子驻车控制（0x305）
    if CC.cruiseControl.cancel:
      can_sends.append(self.packer.make_can_msg("EPB_Control", 0, {
        "EPB_Req": 1,  # 释放驻车
        "EPB_Req_Active": 1,
      }))

    self.frame += 1
    return CC.actuators, can_sends

  # 新增辅助方法 ▼
  def _update_steer_rate_limit(self, current_rate, limit):
    delta = current_rate - limit
    if delta < 0:
      return min(self.steer_rate_limit + 0.1, 1.0)
    else:
      return max(self.steer_rate_limit - 0.2 * delta, 0.0)

  def _modified_stock_accel(self, accel, lead_dist):
    factor = interp(lead_dist, [0, 30, 60], [0.6, 0.8, 1.0])
    modified_accel = clip(accel * factor, -2.0, 2.0)
    if abs(modified_accel - accel) > 0.5:
      cloudlog.info(f"BYD控制: 加速度大幅修正 - 原始:{accel:.2f} 修正后:{modified_accel:.2f}", log_dir=BYD_LOG_PATH)
    return modified_accel  # ▲
