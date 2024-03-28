from ffmpeg_streaming import Formats, Bitrate, Representation, Size

video = ffmpeg_streaming.input("BigBuckBunny.mp4")
dash = video.dash(Formats.h264())
dash.auto_generate_representations()
_144p  = Representation(Size(256, 144), Bitrate(95 * 1024, 64 * 1024))
_240p  = Representation(Size(426, 240), Bitrate(150 * 1024, 94 * 1024))
dash.representations(_144p, _240p)
dash.output('BigBuckBunny.mpd')
