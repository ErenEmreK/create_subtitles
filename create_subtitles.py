#!/usr/bin/env python

import sys
import os

import whisper
import stable_whisper

import pysrt
from webvtt import WebVTT, Caption

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
                         
def subtitles_for_list(model, video_list, sub_dir, sub_extension='.srt', plus_time=0, refine=False, tag=('<font color="#FFFFFF">', '</font>'), use_stable=False, vad=False, language=None):         
    file_count = len(video_list)
    done = 0
    print(f"Creating subtitles for {file_count} files. This may take a while...")
    for video_path in video_list:
          
        sub_base_name = os.path.splitext(os.path.basename(video_path))[0] + sub_extension
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
        
        if sys_args[1] == "-h":
            print("Usage: create_subtitles.py [path/to/input/file.mp4 OR path/to/input/folder] -o [path/to/output/folder] -f [subtitle format] -p [plus time] -m [model size]")
            print("Less verbose usage: create_subtitles.py [path/to/input/file.mp4 OR path/to/input/folder] -s")
            print("Check https://github.com/ErenEmreK/create_subtitles")
            #TODO be more verbose here
            sys.exit()
        
        output_dir = None
        plus_time = 0
        sub_format = '.srt'
        model_size = 'small'
        input_list = []
        use_stable = False
        timestamps = False
        refine = False
        vad = False
        language = None
        
        extensions = ['.mp4', '.mkv', '.mp3', '.wav', '.mpeg', '.m4a', '.webm', '.avi']
        sub_extensions = ['.srt', '.vtt']
        
        i = sys_args[1]
        
        if os.path.isfile(i):
            #we set input folder as output folder by default 
            output_dir = os.path.dirname(i)
            input_list = [i]
        
        elif os.path.isdir(i):
            #we set input folder as output folder by default 
            output_dir = i
            input_list = [os.path.join(i, file) for file in os.listdir(i) if os.path.splitext(file)[1] in extensions]
    
        else:
            print(f"Couldn't reach {i}")
            sys.exit()
            
        for n in range(2, len(sys_args)):
            if sys_args[n] == "-o":
                try:
                    requested_path = sys_args[n + 1] 
                    if os.path.isdir(requested_path):
                        output_dir = requested_path
                    
                    else:
                        print("Requested output directory is invalid.")
                        sys.exit()
                
                except IndexError:
                    print("Output location isn't defined. Creating the files in video folder instead. ")
                    pass
                
            elif sys_args[n] == "-f":
                try:
                    requested_format = sys_args[n + 1] 
                    if requested_format in sub_extensions:
                        sub_format = requested_format
                    else:
                        print("Unable to create requested subtitle format. Supported formats: " + str(sub_extensions))
                        sys.exit()
                except IndexError:
                    pass
    
            elif sys_args[n] == "-p":
                try:
                    plus_time = float(sys_args[n + 1]) 
                except (ValueError, IndexError):
                    print("Plus-time didn't specified properly.")
                    sys.exit()
            
            elif sys_args[n] == "-m":
                model_size_names = ['tiny', 'base', 'small', 'medium', 'large', 'tiny.en',  
                                    'base.en', 'small.en', 'medium.en', 'large.en']
                try:
                    requested_model = sys_args[n + 1] 
                    if requested_model in model_size_names:
                        model_size = requested_model
                    else:
                        print("Requested model is not valid.")
                        print("Possible model names: " + str(model_size_names))
                        sys.exit()
                        
                except IndexError:
                    print("Model keyword did not used properly. ")
                    print("Possible model keywords: " + str(model_size_names))
                    sys.exit()
            
            elif sys_args[n] == "-s":
                use_stable = True
            
            elif sys_args[n] == "-t":
                timestamps = True
            
            elif sys_args[n] == "-r":
                refine = True
            
            elif sys_args[n] == "-v":
                vad = True
                
            elif sys_args[n] == "-l":
                try:
                    language = sys_args[n + 1] 

                except IndexError:
                    print("Language keyword did not used properly. ")
                    sys.exit()
            
    else:
        print("You must enter an input path.")
        sys.exit()
        
    return model_size, input_list, output_dir, sub_format, plus_time, use_stable, timestamps, refine, vad, language
    
def main():

    model_size, input_list, output_dir, sub_format, plus_time, use_stable, timestamps, refine, vad, language = commands(sys.argv)

    model = stable_whisper.load_model(model_size) if use_stable else whisper.load_model(model_size)
        
    tag = ('<font color="#FFFFFF">', '</font>') if sub_format == '.srt' and not timestamps else None

    subtitles_for_list(model, input_list, output_dir, 
                       sub_extension=sub_format, plus_time=plus_time, 
                       refine=refine, tag=tag, 
                       use_stable=use_stable, vad=vad, language=language)
         
if __name__ == '__main__':
    main()