import os

import pysrt
import webvtt

def check_completed(sentence):
    sentence = sentence.strip()
    #We check if sentence ends with punctiation, 
    puncs = ['.', '?', '!']
    try:
        if any(sentence[-i] in puncs for i in range(1, 4)):
            return True
    except IndexError:
        return False
    
    return False
           
def concat_srt(file, out_file=None, char_threshold=160):
    if not out_file:
        out_file = file    
    
    new_subs = pysrt.SubRipFile()
    subs = pysrt.open(file)
    text = ""
    start = False
    
    for index, sub in enumerate(subs):
        text += sub.text.strip() + " "
        if not start:
            start = sub.start
        if check_completed(sub.text) or len(text) >= char_threshold or index == (len(subs) - 1):
            new_subs.append(pysrt.SubRipItem(
                             start=start,
                             end=sub.end,
                             text=text.strip()))
            text = ""
            start = False
        
    new_subs.save(out_file)

def concat_vtt(file, out_file=None, char_threshold=160): 
    if not out_file:
        out_file = file    
    
    new_subs = webvtt.WebVTT()
    subs = webvtt.read(file)
    text = ""
    start = False
    
    for index, sub in enumerate(subs):
        text += sub.text.strip() + " "
        if not start:
            start = sub.start
        if check_completed(sub.text) or len(text) >= char_threshold or index == (len(subs) - 1):
            new_subs.captions.append(webvtt.Caption(
                             start=start,
                             end=sub.end,
                             text=text.strip()))
            text = ""
            start = False
        
    new_subs.save(out_file)
    
def concat_srt_vtt(file, out_file=None, char_threshold=160):
    if os.path.splitext(file)[1] == '.srt':
        concat_srt(file, out_file=None, char_threshold=char_threshold)
        print("Subtitle file concatenated!")
    elif os.path.splitext(file)[1] == '.vtt':
        concat_vtt(file, out_file=None, char_threshold=char_threshold)
        print("Subtitle file concatenated!")
    else:
        print("Unsupported file type. Use srt or vtt. ")