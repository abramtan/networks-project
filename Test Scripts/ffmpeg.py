import ffmpeg_streaming
from ffmpeg_streaming import Formats
import sys
import datetime

video = ffmpeg_streaming.input('./BigBuckBunny-short.mp4')

def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()

hls = video.hls(Formats.h264())
hls.auto_generate_representations([240, 144])
hls.output('./dash/test-9/BigBuckBunny.m3u8', monitor=monitor)