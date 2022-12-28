import json
import jieba
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timestamp_file',
                        '-t',
                        type=str,
                        required=True,
                        help="")
    parser.add_argument('--srt_file',
                        '-s',
                        type=str,
                        required=True,
                        help="")


    args = parser.parse_args()

    return args

class timeConverter:
    def __init__(self, h=0, m=0, s=0, ms=0):
        self.h = h
        self.m = m
        self.s = s
        self.ms = ms

    def carry(self):
        self.s += (self.ms // 1000)
        self.m += (self.s // 60)
        self.h += (self.m // 60)

        self.ms %= 1000
        self.s %= 60
        self.m %= 60

    def clear(self):
        self.ms = 0
        self.s = 0
        self.m = 0
        self.h = 0

    def addByMs(self, ms):
        self.ms += ms
        self.carry()

    def addByS(self, s):
        self.s += s
        self.carry()

    def addByM(self, m):
        self.m += m
        self.carry()

    def addByH(self, h):
        self.h += h
        self.carry()

    def resTimeFormat(self):
        self.carry()
        string = "{:02d}:{:02d}:{:02d},{:03d}".format(self.h, self.m, self.s, self.ms)
        return string


class srtConverter:
    def __init__(self, data_path):
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        self.len = len(self.data)
        self.curTime = timeConverter()
        self.index = list()
        self.sTime = list()
        self.eTime = list()
        self.words = list()

    def findByElement(self, start, end, word):
        index = 0
        for d in self.data:
            if d['start'] == start and d['end'] == end and d['word'] == word:
                return index
            index += 1
        return -1

    def getElementByIndex(self, index):
        if index >= self.len or index < 0:
            return None
        return self.data[index]

    def addSrtByIndex(self, s_index, e_index):
        s_time = timeConverter()
        e_time = timeConverter()
        s = 1e8
        e = 0
        w = ""
        for i in range(s_index, e_index + 1):
            d = self.data[i]
            s = min(int(d['start']), s)
            e = max(int(d['end']), e)
            w += d['word']

        s_time.addByMs(s)
        e_time.addByMs(e)

        if len(self.index) == 0:
            self.index.append(1)
        else:
            idx = self.index[-1]
            self.index.append(idx + 1)

        self.sTime.append(s_time.resTimeFormat())
        self.eTime.append(e_time.resTimeFormat())
        self.words.append(w)


    def dumpToFile(self, filename):
        f = open(filename, 'w')
        for i in range(len(self.index)):
            idx = self.index[i]
            s = self.sTime[i]
            e = self.eTime[i]
            w = self.words[i]
            writeString = ""

            if i != 0:
                writeString += "\n"
            writeString += "{}\n".format(idx)
            writeString += "{} --> {}\n".format(s, e)
            writeString += "{}\n".format(w)

            f.write(writeString)
        f.close()

def main():
    args = parse_args()

    srtObj = srtConverter(args.timestamp_file)

    text = ''
    for d in srtObj.data:
        text += d['word']

    print(text)

    words = list()
    for w in jieba.cut(text, cut_all=False, HMM=True):
        words.append(str(w))
    print(words)

    cur = 0
    s_idx = 0
    e_idx = 0
    word = ""
    for i in range(len(words)):
        word += words[i]
        cur += len(words[i])
        e_idx = cur
        if len(word) > 10 or i == len(words) - 1:
            srtObj.addSrtByIndex(s_idx, e_idx - 1)
            word = ""
            s_idx = cur
    srtObj.dumpToFile(args.srt_file)

if __name__ == '__main__':
    main()
