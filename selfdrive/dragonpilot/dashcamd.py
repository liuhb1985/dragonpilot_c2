import os
import time
import datetime
import cereal.messaging as messaging

DASHCAM_VIDEOS_PATH = '/data/media/0/dashcam/'
DASHCAM_DURATION = 300  # max is 180 (5min)
DASHCAM_BIT_RATES = 4000000  # max is 4000000
DASHCAM_MAX_SIZE_PER_FILE = DASHCAM_BIT_RATES / 8 * DASHCAM_DURATION  # 4Mbps / 8 * 180 = 90MB per 180 seconds (150mb per 300 seconds)
DASHCAM_FREESPACE_LIMIT = 15  # we start cleaning up footage when freespace is below 15%
DASHCAM_KEPT_MIN_SIZE = DASHCAM_MAX_SIZE_PER_FILE * 240  # 12 hrs of video = 21GB (20hrs of video = 36GB)

class Dashcamd():
  def __init__(self):
    self.dashcam_folder_exists = False
    self.dashcam_mkdir_retry = 0
    self.dashcam_next_time = 0
    self.started = False
    self.free_space = 1.

  def run(self, started, free_space):
    self.free_space = free_space
    if self.started and not started:
      self.stop()
    self.started = started
    self.make_folder()
    if self.dashcam_folder_exists:
      self.start()
      self.clean_up()

  def stop(self):
    os.system("killall -SIGINT screenrecord")
    self.dashcam_next_time = 0

  def make_folder(self):
    if not self.dashcam_folder_exists and self.dashcam_mkdir_retry <= 5:
      # create dashcam folder if not exist
      try:
        if not os.path.exists(DASHCAM_VIDEOS_PATH):
          os.makedirs(DASHCAM_VIDEOS_PATH)
        else:
          self.dashcam_folder_exists = True
      except OSError:
        self.dashcam_folder_exists = False
        self.dashcam_mkdir_retry += 1

  def start(self):
    # start recording
    if self.started:
      ts = time.monotonic()
      if ts >= self.dashcam_next_time:
        now = datetime.datetime.now()
        file_name = now.strftime("%Y-%m-%d_%H-%M-%S")
        os.system("LD_LIBRARY_PATH= screenrecord --bit-rate %s --time-limit %s %s%s.mp4 &" % (
          DASHCAM_BIT_RATES, DASHCAM_DURATION, DASHCAM_VIDEOS_PATH, file_name))
        self.dashcam_next_time = ts + DASHCAM_DURATION - 1
    else:
      self.dashcam_next_time = 0

  def clean_up(self):
    # clean up
    if (self.free_space < DASHCAM_FREESPACE_LIMIT) or (self.get_used_spaces() > DASHCAM_KEPT_MIN_SIZE):
      try:
        files = [f for f in sorted(os.listdir(DASHCAM_VIDEOS_PATH)) if os.path.isfile(DASHCAM_VIDEOS_PATH + f)]
        os.system("rm -fr %s &" % (DASHCAM_VIDEOS_PATH + files[0]))
      except (IndexError, FileNotFoundError, OSError):
        pass

  def get_used_spaces(self):
    try:
      val = sum(os.path.getsize(DASHCAM_VIDEOS_PATH + f) for f in os.listdir(DASHCAM_VIDEOS_PATH) if
                os.path.isfile(DASHCAM_VIDEOS_PATH + f))
    except (IndexError, FileNotFoundError, OSError):
      val = 0
    return val
