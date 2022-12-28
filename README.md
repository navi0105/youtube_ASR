# A Subtitles Generator using WeNet Speech

本期末專題為 林育辰、梁俊彥同學於 國立臺灣大學 數位語音處理概論的作品，按照 README 執行後，可於本機開啟網頁，並透過網頁自動以輸入的 YouTube 網址生成有字幕的影片。


## Environment
- `python 3.8`
- `Ubuntu 20.04`
- gdown


## Install Package
```shell
pip install -r requirements.txt
```

## How to build a website
```shell
python api.py -d DEBUG -p 2048
```

接著在網頁上輸入 0.0.0.0:2048 即可使用網頁。

## Decoder Usage
```
python decoder.py \
    --model_dir <model_dir> \
    --url <url> \
    --lang <lang> \
    --decode_text_file <decode_text_file> \
    --enable_timestamp \
    --decode_timestamp_file <decode_timestamp_file>

```
