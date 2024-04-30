import sys
import os

import whisper
import pysrt

def convert_time(seconds):

    hours = int(seconds // 3600)
    remaining_seconds = seconds % 3600
    
    minutes = int(remaining_seconds // 60)
    remaining_seconds %= 60
    
    seconds = int(remaining_seconds)
    miliseconds = int((remaining_seconds - seconds) * 1000)
    
    return (hours, minutes, seconds, miliseconds)

def result_to_srt(result, output_file, glue=False, plus_time=False):
    #We create our srt object
    subs = pysrt.SubRipFile()

    if not glue:
        #If glue method isnt used, we create subtitle instances for every sentence
        #in our result, using its start-end timestamps
        for segment in result['segments']:
            start_time = convert_time(segment['start']) 
            end_time = convert_time(segment['end'])
            
            sub_item = pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=segment['text'])
            subs.append(sub_item)

    else:
        #If glue is used we set end time of instances as start of the next one
        for i in range(len(result['segments']) - 1):
            start_time = convert_time(result['segments'][i]['start'])
            if not plus_time:
                end_time = convert_time(result['segments'][i+1]['start'])
            else:
                #TODO drop second calc altogether, use start time above instead
                #We add plus time to instance to prolong it
                #TODO check
                end_time = convert_time(min(result['segments'][i+1]['start'], 
                                            (result['segments'][i]['end']) + plus_time))
            sub_item = pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=result['segments'][i]['text'])
            subs.append(sub_item)
        last_sub_item = pysrt.SubRipItem(start=convert_time(result['segments'][-1]['start']), 
                                        end=convert_time(result['segments'][-1]['end']), 
                                        text=result['segments'][-1]['text'])
    subs.save(output_file, encoding='utf-8')
    print(f'Subtitle file {output_file} is ready.')   

def subtitles_for_list(model, video_list, sub_path, OUT_ISDIR=False, sub_extension='.srt', glue=False):
    file_count = len(video_list)
    done = 0
    for video_path in video_list:
        result = model.transcribe(video_path)
        if OUT_ISDIR:
            #TODO Just get filename w/o absolute path and create sub_file that way
            sub_file = os.path.splitext(video_path)[0] + sub_extension
            sub_path = os.path.join(sub_path, sub_file)
        else:
            sub_file = sub_path
            
        if os.path.splitext(sub_file)[1] == '.srt':
            result_to_srt(result, sub_path, glue=glue)
            done += 1
            print(f"{done}/{file_count}")
        else:
            #TODO implement other subtitle formats
            print(f"Unable to create {sub_extension} files. Use '.srt' instead.")
            break
    
def get_paths(input, output):
    #TODO handle -e case later
    #TODO optimize
    #We return True if output is folder, False if file (to avoid checking it later)
    OUT_ISDIR = False 
    
    for requested_path in (input, output):
        if not os.path.exists(requested_path):
            print(f"Couldn't reach {requested_path}")
            sys.exit()
    
    if os.path.isfile(input) and os.path.isfile(output):
        i, o = [input], output
        
    elif os.path.isdir(input) and os.path.isdir(output):
        OUT_ISDIR = True
        i, o = [os.path.join(input, file) for file in os.listdir(input)], output
    
    else:
        print("Input and output formats should match. [input_file] [output_file] or [input_folder] [output_folder]")
        sys.exit()
        
    return i, o, OUT_ISDIR
            
def main():
    #1-Assuming you can use "." in CLI: 
    model_names = ['tiny.en', 'base.en', 'small.en', 'medium.en', 'large.en', 
                   'tiny', 'base', 'small', 'medium', 'large']
    #2-Assuming syntax
    model = whisper.load_model(command) if command in model_names for command in sys.argv[2:] else whisper.load_model("small") 
    input_paths, output_path, OUT_ISDIR = get_paths(sys.argv[1], sys.argv[2])
    
    