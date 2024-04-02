#!/usr/bin/python3
# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.
"""
import time
from picamera2 import Picamera2, Preview
from libcamera import Transform
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)},transform=Transform(hflip=1,vflip=1))
picam2.configure(preview_config)
picam2.start_preview(Preview.QTGL)
picam2.opppen
picam2.start()
time.sleep(200)
metadata = picam2.capture_file("image.jpg")
print(metadata)
picam2.close()
"""

from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview
import time
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480)}, lores={"size": (640, 480)}, display="lores")
#video_config = picam2.create_video_configuration(main={"size": (80, 60), "framerate": 20}, lores={"size": (80, 60), "framerate": 20}, display="lores")
picam2.configure(video_config)
#encoder = H264Encoder(bitrate=10000000)
#output = "test.h264"
picam2.start_preview(Preview.QTGL)
#picam2.start_recording(encoder, output)
time.sleep(10)
#picam2.stop_recording()
picam2.stop_preview()