import argparse
import json
import sys
import os
import shutil
import pytube
import subprocess
import torch
import wenetruntime as wenet
from opencc import OpenCC
from tqdm import tqdm
import wave

from tools.video import get_video_wav
from tools.decode import streaming_decode
from tools.segment import sentence_segment


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', 
                        '-u',
                        type=str,
                        required=True,
                        help="Youtube video URL.")
    parser.add_argument('--model_dir',
                        '-m',
                        type=str,
                        default=None,
                        help="Your Wenet Pretrained Model, \
                              not required since decoder will download automatically if not provided.")
    parser.add_argument('--lang',
                        '-l',
                        type=str,
                        default='chs',
                        help="Decode language, Chinese(chs) and English(en) only")
    parser.add_argument('--tmp_dir',
                        type=str,
                        default='tmp/',
                        help="temporary directory for downaload and process youtube video, \
                              directory will be deleted after decode is finished.")
    parser.add_argument('--decode_text_file',
                        type=str,
                        default=None,
                        help="file path for write down decoded text.")
    parser.add_argument('--decode_timestamp_file',
                        type=str,
                        default=None,
                        help="file path for write down decoded timestamp.")
    parser.add_argument('--segment_model', 
                        type=str,
                        default=None,
                        help="Your BERT Sentence Segment Model.")
    

    args = parser.parse_args()

    return args

def load_decoder(args):
    decoder = wenet.Decoder(model_dir=args.model_dir,
                            lang=args.lang,
                            enable_timestamp=True,
                            continuous_decoding=True)

    return decoder

def extract_result(decode_result):
    curr_end_time = -1
    complete_text = ''
    word_timestamp = []

    for result in decode_result:
        curr_text = ''
        best = result["nbest"][-1]
        word_pieces = best["word_pieces"]
        for wp in word_pieces:
            if wp["end"] > curr_end_time:
                curr_text += wp['word']
                word_timestamp.append(wp)
                curr_end_time = wp["end"]

        if curr_text != '':
            complete_text += curr_text + '\n'
    return complete_text, word_timestamp

def main():
    args = parse_args()

    decoder = load_decoder(args)

    get_video_wav(args)

    all_decode_result = streaming_decode(args, decoder)
    complete_text, word_timestamp = extract_result(all_decode_result)
    if args.segment_model is not None:
        assert os.path.exists(args.segment_model)
        complete_text = sentence_segment(complete_text.splitlines(), args.segment_model)

    if args.decode_text_file is not None:
        with open(args.decode_text_file, 'w') as f:
            f.write(complete_text)
    if args.decode_timestamp_file is not None:
        with open(args.decode_timestamp_file, 'w') as f:
            json.dump(word_timestamp, f, indent=2, ensure_ascii=False)

    print("Decode Result:")
    print(complete_text)

    shutil.rmtree(args.tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()