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

def result_to_srt(result, output_file, glue):
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
        for i in range(len(result['segments']) - 1):
            start_time = convert_time(result['segments'][i]['start'])
            end_time = convert_time(result['segments'][i+1]['start'])
            
            sub_item = pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=result['segments'][i]['text'])
            subs.append(sub_item)
        last_sub_item = pysrt.SubRipItem(start=convert_time(result['segments'][-1]['start']), 
                                        end=convert_time(result['segments'][-1]['end']), 
                                        text=result['segments'][-1]['text'])
    subs.save(output_file, encoding='utf-8')
    print(f'Subtitle file {output_file} is ready.')   

def subtitles_for_folder(video_folder, sub_folder, sub_extension='.srt', glue=False):
    files = os.listdir(video_folder)
    file_count = len(files)
    done = 0
    for file in files:
        video_path = os.path.join(video_folder, file)
        result = model.transcribe(video_path)
        
        sub_file = os.path.splitext(video_path)[0] + sub_extension
        sub_path = os.path.join(sub_folder, sub_file)
        if sub_extension == '.srt':
            result_to_srt(result, sub_path, glue=glue)
            done += 1
            print(f"{done}/{file_count}")
        else:
            #TODO implement other subtitle formats
            print(f"Unable to create {sub_extension} files. Use '.srt' instead.")
            break
    
def get_paths(input, output):
    if not os.path.exists(input):
        print(f"Couldn't reach {input}")
        sys.exit()
        
    if os.path.isfile(input):
        i = [input]
    elif os.path.isdir(input):
        i = [os.path.join(input, file) for file in os.listdir(input)]
 
            
def main():
    paths = get_paths(sys.argv[1], sys.argv[2])
     