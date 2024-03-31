import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size
import sys
import datetime

video = ffmpeg_streaming.input('/home/ubuntu/networks_project/BigBuckBunny.mp4')

_144p  = Representation(Size(256, 144), Bitrate(95 * 1024, 64 * 1024)) # 144p alone uses almost 100% CPU

def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()

dash = video.dash(Formats.h264())
dash.representations(_144p)
dash.output('/home/ubuntu/networks_project/dash/test-1/BigBuckBunny.mpd', monitor=monitor)