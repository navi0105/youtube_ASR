import os
import shutil
import subprocess
import pytube


def get_video_wav(args):
    #print("Try to download / convert the video using the provided url.")
    url = args.url
    tmp_dir = args.tmp_dir
    tmp_mp4 = os.path.join(tmp_dir, 'tmp_{}.mp4'.format(args.taskID))
    tmp_wav = os.path.join(tmp_dir, 'tmp_{}.wav'.format(args.taskID))

    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.mkdir(tmp_dir)

    video = pytube.YouTube(url)
    video.streams.filter().get_audio_only().download(filename=tmp_mp4)

    cmd = f"ffmpeg -i {tmp_mp4} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 -f wav {tmp_wav}"
    #video.streams.first().download(filename=tmp_mp4)
    video.streams.get_highest_resolution().download(filename=tmp_mp4)
    subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #print("Finished")
