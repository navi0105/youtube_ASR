from argparse import ArgumentParser
import uuid
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    jsonify,
    render_template,
    session,
    make_response
)
import requests
import time
import os

from werkzeug.utils import secure_filename
from threading import Thread
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw

UPLOAD_FOLDER = './upload/'
ALLOWED_EXTENSIONS = set(['mp4', 'mp3'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024     # 32MB

def time2sec(t):
    arr = t.split(' --> ')
    s1 = arr[0].split(',')
    s2 = arr[1].split(',')
    start = int(s1[0].split(':')[0]) * 3600 + int(s1[0].split(':')
                                                  [1]) * 60 + int(s1[0].split(':')[2]) + float(s1[1]) * 0.001
    end = int(s2[0].split(':')[0]) * 3600 + int(s2[0].split(':')[1]) * \
        60 + int(s2[0].split(':')[2]) + float(s2[1]) * 0.001
    return [start, end]

def text_clip(text, name, font):
    # 建立文字字卡函式
    img_empty = Image.new('RGBA', (640, 360))                 # 產生 RGBA 空圖片
    img = img_empty.copy()      # 複製空圖片
    draw = ImageDraw.Draw(img)  # 建立繪圖物件，並寫入文字
    text_width = 25 * len(text)   # 在 480x240 文字大小 20 狀態下，一個中文字長度約 21px
    draw.text(((640-text_width)/2, 10), text, fill=(255, 255, 255),
              font=font, stroke_width=2, stroke_fill='black')
    img.save(name)              # 儲存


def text_in_video(t, text_img, video, output_list):
    # 建立影片和文字合併的函式
    clip = video.subclip(t[0], t[1])                  # 剪輯影片到指定長度
    text = ImageClip(text_img, transparent=True).set_duration(
        t[1]-t[0])  # 讀取字卡，調整為影片長度
    combine_clip = CompositeVideoClip([clip, text])  # 合併影片和文字
    output_list.append(combine_clip)                 # 添加到影片片段裡

@app.route('/api/srtMergeIntoMovie/<taskID>', methods=['GET', 'POST'])
def srtMergeIntoMovie(taskID):
    #host55_url = r"http://140.112.91.55"

    movieFilename = "{}.mp4".format(taskID)
    movieFilenamePath = "./data/{}.mp4".format(taskID)

    srtFilename = "{}.srt".format(taskID)
    srtFilenamePath = "./static/srt/{}".format(srtFilename)

    count = 0
    while os.path.isfile(srtFilenamePath) == False:
        print(count)
        if count > 500:
            return
        time.sleep(1)
        count += 1
    print("mergeSrt")


    # srtPath = r"{}/asrFile/out.srt/{}".format(host55_url, taskID)
    # r = requests.get(srtPath)
    # open("./data/out_{}.srt".format(taskID), "wb").write(r.content)

    # file = request.files['file']
    # file.save(r"./data/{}".format(movieFilename))

    res_data = {
        'res': True,
    }

    #try:
    START_TIME = time.time()
    while True:
        print("runtime error")
        if os.path.isfile(movieFilenamePath) and os.path.isfile(srtFilenamePath):
            break
        END_TIME = time.time()
        if END_TIME - START_TIME > 1200:
            return "Timeout"
        time.sleep(2)

    f = open(srtFilenamePath, 'r')
    print("open")
    srt = f.read()
    f.close()
    srt_list = srt.split('\n')
    sec = 1
    text = 2
    sec_list = [[0, 0]]
    text_list = ['']

    for i in range(len(srt_list)):
        print(i, "srt_list")
        if i == sec:
            sec = sec + 4
            if sec_list[-1][1] != time2sec(srt_list[i])[0]:
                sec_list.append(
                    [sec_list[-1][1], time2sec(srt_list[i])[0]])
                text_list.append('')
                sec_list.append(time2sec(srt_list[i]))
        if i == text:
            text = text + 4
            text_list.append(srt_list[i])

    # img_empty = Image.new('RGBA', (480, 240))                 # 產生 RGBA 空圖片
    video = VideoFileClip(movieFilenamePath).resize((640, 480))
    #video = VideoFileClip(movieFilenamePath
    #                      ).resize((640, 480))  # 讀取影片，改變尺寸
    video_duration = float(video.duration)                    # 讀取影片總長度
    font = ImageFont.truetype(
        './fonts/NotoSansMonoCJKtc-Regular.otf', 22)   # 設定文字字體和大小
    output_list = []                                          # 記錄最後要組合的影片片段

    # 如果字幕最後的時間小於總長度
    if sec_list[-1][1] != video_duration:
        sec_list.append([sec_list[-1][1], video_duration])     # 添加時間到時間串列
        # text_list.append('')                                  # 添加空字串到文字串列

    while len(sec_list) < len(text_list):
        sec_list.append([video_duration, video_duration])

    while len(sec_list) > len(text_list):
        text_list.append('')

    print("START to generate the text list")
    # 使用 for 迴圈，產生文字字卡
    print(text_list, len(text_list))
    print(sec_list, len(sec_list))
    for i in range(len(text_list)):
        f = open('data/.tmpp_{}'.format(taskID), 'w')
        print('data/.tmpp_{}'.format(taskID))
        f.write(str(round((i + 1) * 100 / len(text_list), 0)))
        f.close()

        text_clip(text_list[i], 'srt.png', font)
        text_in_video(sec_list[i], 'srt.png', video, output_list)

    print("START to output")
    finishFilename = "{}.mp4".format(taskID)
    output = concatenate_videoclips(output_list)      # 合併所有影片片段
    output.write_videofile(finishFilename, temp_audiofile="temp-audio.m4a",
                           remove_temp=True, codec="libx264", audio_codec="aac")

    os.rename(finishFilename, "./static/video/{}".format(finishFilename))

    # srtFilename = "out_{}.srt".format(taskID)
    # movieFilename = "movie_{}.mp4".format(taskID)
    # os.rename("./data/{}".format(srtFilename),
    #           "./static/srt/{}".format(srtFilename))
    # os.rename("./data/{}".format(movieFilename),
    #           "./static/video/{}".format(movieFilename))
    print('ok')
    #except:
    #    res_data['res'] = False

    #finally:
    #    return res_data

@app.route('/detect', methods=['GET'])
def detect(userId):
    url = "http://140.112.91.55/asrFile/out.srt/{}".format(userId)

    START_TIME = time.time()
    while True:
        r = requests.get(url)
        status = r.text.split()[0]
        time.sleep(2)
        if status != "404":
            break
        END_TIME = time.time()
        if END_TIME - START_TIME > 1200:
            break

    r = requests.get(url)
    open("./data/out_{}.srt".format(userId), "wb").write(r.content)
    fileBinary = open("./data/movie_{}.mp4".format(userId), "rb")
    host57_url = r"http://140.112.91.57:615"
    r = requests.post(
        r"{}/api/srtMergeIntoMovie/{}".format(host57_url, userId), files={'file': fileBinary})
    r = requests.get(
        r"{}/static/video/movie_{}_finish.mp4".format(host57_url, userId))
    open("./static/video/movie_{}_finish.mp4".format(userId), "wb").write(r.content)
    os.rename("./data/out_{}.srt".format(userId),
              "./static/srt/out_{}.srt".format(userId))
    os.rename("./data/movie_{}.mp4".format(userId),
              "./static/video/movie_{}.mp4".format(userId))


@app.route('/url_send', methods=['POST'])
def url_send_api():
    data = {
        'user': request.form['user']
    }
    r = requests.post("http://140.112.91.55/submit", data=data)
    userId = str(r.text.split('<p id="userid">')[1].split('<')[0])

    html = """
        <iframe width=800 height=1000 src="http://140.112.91.55/wait/{}"></iframe>
    """.format(userId)

    thr = Thread(target=detect, args=[userId])
    thr.start()

    return html


def allowed_file(filename):
    return '.' in filename and\
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@ app.route('/srtConverter/<taskID>', methods=['POST'])
def srt_converter(taskID):
    decode_timestamp_file = "./data/decoder_{}.json".format(taskID)
    srt_file = "./static/srt/{}.srt".format(taskID)
    count = 0
    while os.path.isfile(decode_timestamp_file) == False:
        if count > 500:
            return
        time.sleep(1)
        count += 1
    print("srtConverter")

    f = os.popen(
        "python3 srtConverter.py --timestamp_file '{}' --srt_file '{}'".format(decode_timestamp_file, srt_file))
    f.close()

    srtMergeIntoMovie(taskID)

@ app.route('/submit', methods=['GET', 'POST'])
def send_youtubeUrl_api():
    url = request.form['text']
    taskID = uuid.uuid4().hex
    print("url", url)

    #print(request.values.get('sendYoutubeUrl', None))
    data = {
        'taskID': "{}".format(taskID),
    }
    #render = make_response(render_template("app.html", data=data))

    #render.set_cookie(key='taskID', value=taskID,
    #                  expires=time.time() + 6 * 60)
    thr = Thread(target=decoder, args=[url, taskID])
    thr.start()

    return render_template("app.html", data=data)



@app.route('/decode', methods=['GET', 'POST'])
def decoder(url, taskID):
    decode_timestamp_file = "./data/decoder_{}.json".format(taskID)
    f = os.popen(
        "python3 decoder.py --url '{}' --decode_timestamp_file '{}' --taskID '{}' --model_dir wenetspeech_conformer_finetune_exp".format(url, decode_timestamp_file, taskID))
    #f = os.popen(
    #    "python3 decoder.py --url '{}' --decode_timestamp_file '{}' --taskID '{}'".format(url, decode_timestamp_file, taskID))
    f.close()

    while os.path.isfile("tmp/tmp_{}.mp4".format(taskID)) == False:
        time.sleep(1)
    os.rename("tmp/tmp_{}.mp4".format(taskID), "data/{}.mp4".format(taskID))

    #thr = Thread(target=srt_converter, args=[taskID])
    srt_converter(taskID)
    #thr.start()

    #while os.path.isfile(decode_timestamp_file) == False:
    #    time.sleep(1)
    #os.rename(decode_timestamp_file, "data/{}".format(decode_timestamp_file))

@app.route('/check/<taskID>', methods=['POST'])
def checkProgress(taskID):
    print("test")
    path = r"./static/video/movie_{}_finish.mp4".format(taskID)
    data = dict()

    data['state'] = "initial"

    progressFile = "./data/.tmp_{}".format(taskID)
    if os.path.isfile(progressFile):
        f = open(progressFile, 'r')
        for d in f.readlines():
            data['decode_progress'] = float(d)
            data['state'] = "decoding"
        f.close()

    decode_timestamp_file = "./data/decoder_{}.json".format(taskID)
    if os.path.isfile(decode_timestamp_file):
        data['state'] = "decoded"

    srt_file = "./static/srt/{}.srt".format(taskID)
    if os.path.isfile(srt_file):
        data['state'] = "srtComplete"

    subtitlesProgressFile = "./data/.tmpp_{}".format(taskID)
    if os.path.isfile(subtitlesProgressFile):
        f = open(subtitlesProgressFile, 'r')
        for d in f.readlines():
            data['subtitles_progress'] = float(d)
            data['state'] = "subtitlesProcessing"
        f.close()

    movieFinishFile = "./static/video/{}.mp4".format(taskID)
    if os.path.isfile(movieFinishFile):
        data['state'] = "complete"

    return data


@app.route('/checkMovie/<userId>', methods=['POST'])
def isCheckMovie(userId):
    path = r"./static/video/movie_{}_finish.mp4".format(userId)
    data = {
        'res': False,
    }
    if os.path.isfile(path):
        data['res'] = True
    return data


@app.route("/<taskID>/preview")
def show_userId_video(taskID):
    html = """
            <center>
            <video width=640 height=480 controls="controls">
                <source src="../static/video/{}.mp4" type="video/mp4" />
            </video>

            </center>
    """.format(taskID)

    return html


@app.route("/")
def home():
    data = {
        'dataId': '000000',
        'isStartWait': False,
    }
    return render_template("app.html", data=data)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'

    )
    arg_parser.add_argument('-p', '--port', default=614, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True

    app.run(host='0.0.0.0', port=options.port,
            debug=options.debug, threaded=True, processes=True)
