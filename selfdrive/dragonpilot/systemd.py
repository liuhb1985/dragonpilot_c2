#!/usr/bin/env python3
#pylint: disable=W0105
# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
This is a service that broadcast dp config values to openpilot's messaging queues
'''

import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.selfdrive.dragonpilot.dashcamd import Dashcamd

HERTZ = 1

def confd_thread():
  sm = messaging.SubMaster(['deviceState'])
  frame = 0
  started = False
  free_space = 1.
  dashcamd = Dashcamd()
  rk = Ratekeeper(HERTZ, print_delay_threshold=None)  # Keeps rate at 2 hz
  while True:
    '''
    ===================================================
    load thermalState data every 3 seconds
    ===================================================
    '''
    if frame % (HERTZ * 3) == 0:
      sm.update(0)
      if sm.updated['deviceState']:
        started = sm['deviceState'].started
        free_space = sm['deviceState'].freeSpacePercent
    '''
    ===================================================
    dashcam
    ===================================================
    '''
    if Params().get_bool("dp_on_road_dashcam") and frame % HERTZ == 0:
      dashcamd.run(started, free_space)
    '''
    ===================================================
    finalise
    ===================================================
    '''
    frame += 1
    rk.keep_time()

def main():
  confd_thread()

if __name__ == "__main__":
  main()
