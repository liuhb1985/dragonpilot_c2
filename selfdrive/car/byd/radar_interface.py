#!/usr/bin/env python3
from cereal import car
from opendbc.can.parser import CANParser
from openpilot.selfdrive.car.byd.values import DBC, CANBUS, CAR, BYD_LOG_PATH
from openpilot.selfdrive.car.interfaces import RadarInterfaceBase
from openpilot.common.params import Params
from openpilot.system.swaglog import cloudlog
import time

# 比亚迪使用77GHz毫米波雷达，目标ID范围0x500-0x538
RADAR_MSGS_A = list(range(0x500, 0x538, 4))
RADAR_MSGS_B = list(range(0x501, 0x539, 4))
NUM_POINTS = len(RADAR_MSGS_A)

def get_radar_can_parser(CP):
  messages = [
    ('Radar_Status', 10),  # 雷达状态报文
  ]
  
  # 目标数据报文（距离和速度信息分开）
  for i in range(NUM_POINTS):
    msg_id_a = f"RADAR_TRACK_{RADAR_MSGS_A[i]:x}"  # 转换为16进制字符串作为消息名
    msg_id_b = f"RADAR_TRACK_{RADAR_MSGS_B[i]:x}"
    messages.extend([
      (msg_id_a, 50),  # 距离/方位角信息
      (msg_id_b, 50),  # 速度/加速度信息
    ])

  return CANParser(DBC[CP.carFingerprint]['radar'], messages, CANBUS.radar)

class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.rcp = get_radar_can_parser(CP)
    self.updated_messages = set()
    self.track_id = 0
    self.trigger_msg = 0x538 if CP.carFingerprint == CAR.BYD_HAN_EV_20 else 0x884
    self.mrr_mode = CP.carFingerprint in [CAR.BYD_HAN_DM_20]
    
    # 记录初始化信息
    cloudlog.info(f"BYD雷达: 初始化 - 车型: {CP.carFingerprint}, MRR模式: {self.mrr_mode}", log_dir=BYD_LOG_PATH)
    self.last_log_time = time.time()
    self.log_interval = 5.0

  def update(self, can_strings):
    ret = car.RadarData.new_message()
    
    values = self.rcp.update_strings(can_strings)
    if not values:
      return super().update(None)

    status = self.rcp.vl['Radar_Status']
    ret.errors = []
    if status['HW_Fault'] or status['Sensor_Dirty']:
      ret.errors.append('fault')
      cloudlog.warning(f"BYD雷达: 故障 - 硬件: {status['HW_Fault']}, 脏污: {status['Sensor_Dirty']}", log_dir=BYD_LOG_PATH)
    
    if not self.rcp.can_valid:
      ret.errors.append('canError')
      cloudlog.error("BYD雷达: CAN通信错误", log_dir=BYD_LOG_PATH)

    # 解析目标数据
    for i in range(NUM_POINTS):
      a_msg = self.rcp.vl[RADAR_MSGS_A[i]]
      b_msg = self.rcp.vl[RADAR_MSGS_B[i]]
      
      if a_msg['Valid'] != 1:
        continue

      if i not in self.pts:
        self.pts[i] = car.RadarData.RadarPoint.new_message()
        self.pts[i].trackId = self.track_id
        self.track_id += 1

      # 单位转换（BYD使用厘米和0.1度为单位）
      self.pts[i].dRel = a_msg['Dist'] / 100.0  # 米
      self.pts[i].yRel = a_msg['Azimuth'] * 0.01745  # 弧度 
      self.pts[i].vRel = b_msg['Speed'] / 3.6  # 米/秒
      self.pts[i].aRel = b_msg['Accel'] * 0.1  # 米/秒²

    # 改进目标处理逻辑 ▼
    if self.mrr_mode:
        # 处理MRR雷达格式
        mrr = self.rcp.vl['RADAR_MRR']
        if mrr['IsValid']:
            self._update_mrr_point(mrr)
    else:
        # 原有处理逻辑增强
        for i in range(NUM_POINTS):
            a_msg = self.rcp.vl[f"RADAR_TRACK_{RADAR_MSGS_A[i]:x}"]  # 修正消息名称格式
            b_msg = self.rcp.vl[f"RADAR_TRACK_{RADAR_MSGS_B[i]:x}"]
            
            if not a_msg['Valid']:  # 统一有效性检查
                continue
                
            if i not in self.pts:
                self.pts[i] = car.RadarData.RadarPoint.new_message()
                self.pts[i].trackId = self.track_id
                self.track_id += 1
            
            # 单位转换
            self.pts[i].dRel = a_msg['Dist'] / 100.0
            self.pts[i].yRel = a_msg['Azimuth'] * 0.01745
            self.pts[i].vRel = b_msg['Speed'] / 3.6
            self.pts[i].aRel = b_msg['Accel'] * 0.1
    
    # 新增目标数量限制 ▼
    ret.points = list(self.pts.values())[:16]  # 最多16个目标
    # ▲
    # 定期记录目标信息
    current_time = time.time()
    if current_time - self.last_log_time > self.log_interval:
        cloudlog.info(f"BYD雷达: 目标数量 {len(ret.points)}", log_dir=BYD_LOG_PATH)
        
        if len(ret.points) > 0:
            closest_point = min(ret.points, key=lambda p: p.dRel)
            cloudlog.info(f"BYD雷达: 最近目标 - ID:{closest_point.trackId} 距离:{closest_point.dRel:.1f}m 速度:{closest_point.vRel:.1f}m/s", 
                         log_dir=BYD_LOG_PATH)
        self.last_log_time = current_time

    return ret

  def _update_mrr_point(self, mrr):
    """处理MRR雷达数据"""
    pt = car.RadarData.RadarPoint.new_message()
    pt.trackId = self.track_id
    pt.dRel = mrr['LongDist']
    pt.yRel = mrr['LatDist']
    pt.vRel = mrr['LongSpeed'] / 3.6
    pt.aRel = mrr['LongAccel'] * 0.1
    pt.measured = True
    self.pts[self.track_id] = pt
    self.track_id = (self.track_id + 1) % 3  # MRR最多跟踪3个目标
