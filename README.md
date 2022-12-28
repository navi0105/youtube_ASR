# Youtube Video ASR

## Introduction
抓取 Youtube 影片並對影片進行 ASR，辨別語音內容的同時獲取對應之 Timestamp。

## Environment
`python 3.8`

## Install Package
```shell
pip install -r requirement.txt
```

## Usage
```
python decoder.py \
    --model_dir <model_dir> \
    --url <url> \
    --lang <lang> \
    --decode_text_file <decode_text_file> \
    --decode_timestamp_file <decode_timestamp_file>

```
