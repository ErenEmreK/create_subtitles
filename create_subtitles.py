#!/usr/bin/env python

import sys
import os
import argparse

import requests
import whisper
import stable_whisper

import pysrt
from webvtt import WebVTT, Caption

def check_link(link):
    try:
        r = requests.get(link)
        if r.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def convert_time(seconds):

    hours = int(seconds // 3600)
    remaining_seconds = seconds % 3600
    
    minutes = int(remaining_seconds // 60)
    remaining_seconds %= 60
    
    seconds = int(remaining_seconds)
    miliseconds = int((remaining_seconds - seconds) * 1000)
    
    return (hours, minutes, seconds, miliseconds)

def result_to_srt_vtt(result, output_file, plus_time=0):
    srt = True if os.path.splitext(output_file)[1] == '.srt' else False
    if srt:
        subs = pysrt.SubRipFile()
    else:
        subs = WebVTT()
   
    for i in range(len(result['segments']) - 1):
        start_time = convert_time(result['segments'][i]['start'])
        end_time = convert_time(min(result['segments'][i+1]['start'], 
                                    (result['segments'][i]['end']) + plus_time))
        text = result['segments'][i]['text']
        
        if srt:
            sub_item = pysrt.SubRipItem(start=start_time, 
                                    end=end_time, 
                                    text=text)
            subs.append(sub_item)
        else:
            sub_item = Caption(
            f'{start_time[0]:02d}:{start_time[1]:02d}:{start_time[2]:02d}.{start_time[3]:03d}',
            f'{end_time[0]:02d}:{end_time[1]:02d}:{end_time[2]:02d}.{end_time[3]:03d}', text)
            
            subs.captions.append(sub_item)
    
    start_time = convert_time(result['segments'][-1]['start'])
    end_time = convert_time(result['segments'][-1]['end'])
    text = result['segments'][-1]['text']
    
    if srt:
        subs.append(pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=text))
        
        subs.save(output_file, encoding='utf-8')
    else:
        subs.captions.append(Caption(
        f'{start_time[0]:02d}:{start_time[1]:02d}:{start_time[2]:02d}.{start_time[3]:03d}',
        f'{end_time[0]:02d}:{end_time[1]:02d}:{end_time[2]:02d}.{end_time[3]:03d}',
        text))
        
        subs.save(output_file)
        
    print(f'Subtitle file {output_file} is ready.')   

def stable_result_to_srt_vtt(result, output_file, plus_time=0):
    
    srt = True if os.path.splitext(output_file)[1] == '.srt' else False
    if srt:
        subs = pysrt.SubRipFile()
    else:
        subs = WebVTT()
   
    for i in range(len(result) - 1):
        start_time = convert_time(result[i].start)
        end_time = convert_time(min(result[i+1].start, result[i].end + plus_time))
        text = result[i].text
        if srt:
            sub_item = pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=text)
            subs.append(sub_item)
        else:
            sub_item = Caption(
            f'{start_time[0]:02d}:{start_time[1]:02d}:{start_time[2]:02d}.{start_time[3]:03d}',
            f'{end_time[0]:02d}:{end_time[1]:02d}:{end_time[2]:02d}.{end_time[3]:03d}', text)
            
            subs.captions.append(sub_item)
    
    start_time = convert_time(result[-1].start)
    end_time = convert_time(result[-1].end)
    text = result[-1].text
    
    if srt:    
        subs.append(pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=text))
        
        subs.save(output_file, encoding='utf-8')
    else:
        
        subs.captions.append(Caption(
        f'{start_time[0]:02d}:{start_time[1]:02d}:{start_time[2]:02d}.{start_time[3]:03d}',
        f'{end_time[0]:02d}:{end_time[1]:02d}:{end_time[2]:02d}.{end_time[3]:03d}',
        text))
        
        subs.save(output_file)
        
    print(f'Subtitle file {output_file} is ready.') 
                         
def subtitles_for_list(model, video_list, sub_dir, sub_extension='.srt', plus_time=0, refine=False, tag=('<font color="#FFFFFF">', '</font>'), use_stable=False, vad=False, language=None, is_url=False):         
    file_count = len(video_list)
    done = 0
    print(f"Creating subtitles for {file_count} files. This may take a while...")
    for video_path in video_list:
          
        sub_base_name = os.path.splitext(os.path.basename(video_path))[0] if not is_url else str(done)
        sub_base_name += sub_extension
        sub_file = os.path.join(sub_dir, sub_base_name)
        
        if use_stable:
            result = model.transcribe(video_path, vad=vad, language=language)
            if refine:
                result = model.refine(video_path, result)
                
            if not plus_time:
                if sub_extension == '.srt' or sub_extension == '.vtt':
                    result.to_srt_vtt(sub_file, tag=tag)
                    done += 1
                    print(f"{done}/{file_count}")
                else:
                    print(f"Unable to create {sub_extension} files. ")
                    sys.exit()
            
            else:
                if sub_extension == '.srt' or sub_extension == '.vtt':
                    stable_result_to_srt_vtt(result, sub_file, plus_time=plus_time)
                    done += 1
                    print(f"{done}/{file_count}")
                else:
                    print(f"Unable to create {sub_extension} files. ")
                    sys.exit()
                
        else:
            result = model.transcribe(video_path, language=language)
            
            if sub_extension == '.srt' or sub_extension == '.vtt':
                result_to_srt_vtt(result, sub_file, plus_time=plus_time)
                done += 1
                print(f"{done}/{file_count}")
            else:
                print(f"Unable to create {sub_extension} files. ")
                sys.exit()
        
def commands(sys_args):
    
    if len(sys_args) >= 2:
        
        parser = argparse.ArgumentParser(
        description="Create subtitles for video/audio files or a folder of such files."
    )
        parser.add_argument("input", help="Path to input file or folder, or URL")
        parser.add_argument("-o", "--output", help="Path to output folder", default=None)
        parser.add_argument("-f", "--format", help="Subtitle format", choices=['.srt', '.vtt'], default='.srt')
        parser.add_argument("-p", "--plus-time", type=float, help="Additional time in seconds to add to subtitles", default=0)
        parser.add_argument("-m", "--model", help="Model size", choices=['tiny', 'base', 'small', 'medium', 'large', 'tiny.en', 'base.en', 'small.en', 'medium.en', 'large.en'], default='small')
        parser.add_argument("-s", "--stable", action="store_true", help="Use stable whisper model for better performance")
        parser.add_argument("-t", "--timestamps", action="store_true", help="Include timestamps")
        parser.add_argument("-r", "--refine", action="store_true", help="Refine subtitles")
        parser.add_argument("-v", "--vad", action="store_true", help="Use VAD")
        parser.add_argument("-l", "--language", help="Specify language")

        args = parser.parse_args(sys_args[1:])
    
        output_dir = os.getcwd()
        input_list = []
        is_url = False
         
        if os.path.isfile(args.input):
            #we set input folder as output folder by default 
            output_dir = args.output if args.output else os.path.dirname(args.input)
            input_list = [args.input]
        
        elif os.path.isdir(args.input):
            #we set input folder as output folder by default 
            output_dir = args.output if args.output else args.input
            extensions = ['.mp4', '.mkv', '.mp3', '.wav', '.mpeg', '.m4a', '.webm', '.avi']
    
            input_list = [os.path.join(args.input, file) for file in os.listdir(args.input) if os.path.splitext(file)[1] in extensions]

        elif check_link(args.input):
            input_list = [args.input]
            is_url = True
            
        else:
            print(f"Couldn't reach {args.input}")
            sys.exit()
            
        if not os.path.isdir(output_dir):
            print("Requested output directory is invalid.")
            sys.exit()
        
    return args.model, input_list, output_dir, args.format, args.plus_time, args.stable, args.timestamps, args.refine, args.vad, args.language, is_url
    
def main():

    model_size, input_list, output_dir, sub_format, plus_time, use_stable, timestamps, refine, vad, language, is_url = commands(sys.argv)

    model = stable_whisper.load_model(model_size) if use_stable else whisper.load_model(model_size)
        
    tag = ('<font color="#FFFFFF">', '</font>') if sub_format == '.srt' and not timestamps else None

    subtitles_for_list(model, input_list, output_dir, 
                       sub_extension=sub_format, plus_time=plus_time, 
                       refine=refine, tag=tag, 
                       use_stable=use_stable, vad=vad, language=language, is_url=is_url)
         
if __name__ == '__main__':
    main()