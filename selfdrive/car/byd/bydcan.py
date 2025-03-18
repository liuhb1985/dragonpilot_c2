import crcmod
from openpilot.common.numpy_fast import clip, interp
from openpilot.selfdrive.car.byd.values import CAR, CarControllerParams, BYD_LOG_PATH
from openpilot.system.swaglog import cloudlog

class BYDCAN:
  def __init__(self, packer):
    self.packer = packer
    self.crc = crcmod.predefined.Crc('crc-8')  # BYD使用CRC-8校验
    cloudlog.info("BYD报文: CAN通信初始化", log_dir=BYD_LOG_PATH)

  def create_steering_control(self, torque, enabled, counter, CP):
    """生成EPS转向控制报文（0x2A4）"""
    values = {
      "Steer_Req": 1 if enabled else 0,
      "Steer_Tq_Req": torque,
      "Steer_Control_Counter": counter % 16,
      "Steer_Checksum": 0,
      "EPS_Reserved1": 0x1,  # 固定值
      "EPS_Reserved2": 0xF if CP.carFingerprint == CAR.HAN_EV_20 else 0x0,
    }
    
    # 使用通用校验算法替代单独实现
    dat = bytes([values["Steer_Req"], 
                values["Steer_Tq_Req"],
                values["Steer_Control_Counter"],
                values["EPS_Reserved1"]])
    
    values["Steer_Checksum"] = byd_checksum(0x2A, dat)  # 使用报文ID作为key
    cloudlog.debug(f"BYD报文: 转向控制 - 力矩:{torque} 使能:{enabled}", log_dir=BYD_LOG_PATH)
    return self.packer.make_can_msg("EPS_Control", 0, values)

  def create_epb_control(self, release):
    """生成电子驻车控制报文（0x305）"""
    return self.packer.make_can_msg("EPB_Control", 0, {
      "EPB_Req": 1 if release else 0,
      "EPB_Req_Active": 1,
    })

  def create_accel_control(self, accel_pct, enabled, counter):
    """生成加速控制报文（0x121）"""
    values = {
      "Accel_Pedal_Pos": int(accel_pct * 100),
      "ACC_Enable": 1 if enabled else 0,
      "ACC_Counter": counter % 256,
      "ACC_Checksum": self.crc_calculate(accel_pct, counter)
    }
    cloudlog.debug(f"BYD报文: 加速控制 - 油门:{accel_pct:.2f} 使能:{enabled}", log_dir=BYD_LOG_PATH)
    return self.packer.make_can_msg("VCU_Accel_Control", 0, values)


  def crc_calculate(self, accel, counter):
    """计算加速控制报文的CRC校验值"""
    self.crc.reset()  # 重置CRC计算器
    data = bytes([int(accel * 100), counter % 256])
    self.crc.update(data)
    return self.crc.digest()[0]
    
  def create_acc_command(self, accel, lead_dist, active, counter):
    """生成ACC控制报文（0x121）"""
    adjusted_accel = self._adjust_accel_curve(accel, lead_dist)
    values = {
      "AccelCmd": adjusted_accel,
      "JerkUpperLimit": 0.15 if lead_dist > 50 else 0.25,
      "JerkLowerLimit": -0.3 if lead_dist > 50 else -0.5,
      "AccControlActive": active,
      "Counter": counter % 256,
      "ACC_Checksum": self.crc_calculate(accel, counter)
    }
    cloudlog.debug(f"BYD报文: ACC命令 - 加速度:{adjusted_accel:.2f} 前车距离:{lead_dist:.1f}", log_dir=BYD_LOG_PATH)
    return self.packer.make_can_msg("ACC_CMD", 0, values)

  def _adjust_accel_curve(self, accel, lead_dist):
    """动态调整加速曲线"""
    factor = interp(lead_dist, CarControllerParams.ACCEL_BP, CarControllerParams.ACCEL_V)
    adjusted = clip(accel * factor, -2.0, 2.0)
    if abs(adjusted - accel) > 0.5:
      cloudlog.info(f"BYD报文: 加速度修正 - 原始:{accel:.2f} 修正:{adjusted:.2f} 系数:{factor:.2f}", log_dir=BYD_LOG_PATH)
    return adjusted

  def create_ui_command(self, chime, left_lane, right_lane, counter):  # 添加counter参数
      """生成UI控制报文（0x316）"""
      values = {
        "LeftLaneState": left_lane + 1,
        "RightLaneState": right_lane + 1,
        "LKAS_AlarmType": chime,
        "LKAS_Problem": 0,
        "LKAS_Off": 0,
        "Solid_Lanes": 1 if (left_lane > 0 and right_lane > 0) else 0,
        "Dashed_Lanes": 1 if (left_lane > 0 or right_lane > 0) else 0,
        "Counter": counter % 4,
        "Checksum": 0,
      }
      
      # 计算校验和
      dat = bytes([
        values["LeftLaneState"],
        values["RightLaneState"],
        values["LKAS_AlarmType"],
        values["Counter"]
      ])
      values["Checksum"] = byd_checksum(0x31, dat)  # 0x31是LKAS_HUD的ID前缀
      
      cloudlog.debug(f"BYD报文: UI状态 - 左线:{left_lane} 右线:{right_lane} 报警:{chime}", log_dir=BYD_LOG_PATH)
      return self.packer.make_can_msg("LKAS_HUD", 0, values)


# 在类外添加通用校验算法
def byd_checksum(byte_key, dat):
    """通用BYD校验算法"""
    first = sum(byte >> 4 for byte in dat) + (byte_key & 0xF)
    second = sum(byte & 0xF for byte in dat) + (byte_key >> 4)
    return ((0x9 - (first % 0x10)) << 4) | (0x9 - (second % 0x10))