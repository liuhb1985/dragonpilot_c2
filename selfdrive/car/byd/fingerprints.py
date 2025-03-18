from cereal import car
from openpilot.selfdrive.car.byd.values import CAR

Ecu = car.CarParams.Ecu

FINGERPRINTS = {
  CAR.BYD_HAN_DM_20: [{
    0x55: 8, 0x8c: 8, 0xd5: 8, 0x101: 8, 0x115: 6, 
    0x130: 8, 0x287: 5, 0x2a4: 8, 0x301: 8, 0x305: 6, 0x310: 8, 0x316: 8,
    0x578: 8, 0x790: 8, 0x792: 8, 0x834: 8, 0x884: 8, 0x1048: 8,
  }],
  CAR.BYD_HAN_EV_20: [{
    0x85: 8, 0x287: 5, 0x301: 8, 0x578: 8, 0x790: 8, 0x813: 8, 0x834: 8,
    0x884: 8, 0x1048: 8, 0x108: 8, 0x121: 8, 0x122: 8, 0x2a4: 8,
    0x316: 8, 0x310: 8, 0x115: 6
  }],
}

FW_VERSIONS = {
  CAR.BYD_HAN_EV_20: {
    (Ecu.eps, 0x18DA30F1, None): [b'BYD-EPS-2020'],
    (Ecu.fwdRadar, 0x762, None): [b'BYD-RADAR-3.0'],
    (Ecu.fwdCamera, 0x745, None): [b'BYD-CAMERA-4.0'],
  },
  
  CAR.BYD_HAN_DM_20: {
    (Ecu.eps, 0x18DA30F1, None): [b'V1.21', b'V1.22'],
    (Ecu.abs, 0x18DA28F1, None): [b'V1.32'],
    (Ecu.fwdCamera, 0x18DA50F1, None): [b'V1.25'],
  },
}
