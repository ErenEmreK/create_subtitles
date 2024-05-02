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

def result_to_srt(result, output_file, plus_time=0):
    #We create our srt object
    subs = pysrt.SubRipFile()

    if not plus_time:
        #If plus-time method isnt used, we create subtitle instances for every sentence
        #in our result, using its start-end timestamps
        for segment in result['segments']:
            start_time = convert_time(segment['start']) 
            end_time = convert_time(segment['end'])
            
            sub_item = pysrt.SubRipItem(start=start_time, 
                                        end=end_time, 
                                        text=segment['text'])
            subs.append(sub_item)

    else:
        #If plus-time is used we set end time of instances as start of the next one
        for i in range(len(result['segments']) - 1):
            start_time = convert_time(result['segments'][i]['start'])
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

def subtitles_for_list(model, video_list, sub_path, plus_time=0, sub_extension='.srt'):
    file_count = len(video_list)
    done = 0
    for video_path in video_list:
        result = model.transcribe(video_path)
        if os.path.isdir(sub_path):
            sub_file = os.path.splitext(video_path)[0] + sub_extension
        else:
            if file_count <= 1:
                sub_file = os.path.splitext(sub_path)[0] + sub_extension
            else: 
                print("Can't write multiple medias to one subtitle file. Creating subtitles in media's location instead.")
                sub_file = os.path.splitext(video_path)[0] + sub_extension
                
        if sub_extension == '.srt':
            result_to_srt(result, sub_path, plus_time=plus_time)
            done += 1
            print(f"{done}/{file_count}")
        else:
            #TODO implement other subtitle formats
            print(f"Unable to create {sub_extension} files. Use '.srt' instead.")
            break
          
def get_commands(sys_args):
    
    if len(sys_args) >= 2:
        
        output_path = None
        plus_time = 0
        sub_format = '.srt'
        model_size = 'small'
        input_list = []
        
        extensions = ['.mp4', '.mkv', '.mp3', '.wav', '.mpeg', '.m4a', '.webm']
        sub_extensions = ['.srt']
        
        i = sys_args[1]
        
        if os.path.isfile(i):
            #we set input folder as output folder by default 
            output_path = os.path.dirname(i)
            input_list = [i]
        
        elif os.path.isdir(i):
            #we set input folder as output folder by default 
            output_path = i
            input_list = [os.path.join(i, file) for file in os.listdir(i) if os.path.splitext(file)[1] in extensions]
    
        else:
            print(f"Couldn't reach {i}")
            sys.exit()
            
        for n in len(range(sys_args)):
            if sys_args[n] == "-o":
                try:
                    requested_path = sys_args[n + 1] 
                    if os.path.isdir(requested_path):
                        output_path = requested_path
                    elif os.path.isfile(requested_path) and os.path.splitext(requested_path)[1] in sub_extensions:
                        print(os.path.splitext(requested_path)[1])
                        output_path = requested_path
                        sub_format = os.path.splitext(requested_path)[1]
                    else:
                        print("Requested output path is invalid or includes non-supported format. Supported formats: " + str(sub_extensions))
                        sys.exit()
                
                except IndexError:
                    print("Output location isn't defined. Creating the files in video folder instead. ")
                    pass
                
            if sys_args[n] == "-f":
                try:
                    requested_format = sys_args[n + 1] 
                    if requested_format in sub_extensions:
                        sub_format = requested_format
                    else:
                        print("Unable to create requested subtitle format. Supported formats: " + str(sub_extensions))
                        sys.exit()
                except IndexError:
                    pass
    
            if sys_args[n] == "-p":
                try:
                    plus_time = int(n + 1) 
                except (ValueError, IndexError):
                    print("Plus-time didn't specified properly.")
                    sys.exit()
            
            if sys_args[n] == "-m":
                model_size_names = ['tiny.en', 'base.en', 'small.en', 'medium.en', 'large.en', 
                                    'tiny', 'base', 'small', 'medium', 'large']
                try:
                    requested_model = sys_args[n + 1] 
                    if requested_model in model_size_names:
                        model_size = requested_model
                except IndexError:
                    print("Model keyword did not used properly. ")
                    print("Possible model keywords: " + str(model_size_names))
                    sys.exit()
        
            
        return model_size, input_list, output_path, sub_format, plus_time
    
    else:
        print("You must enter an input path.")
        sys.exit()
        
 
    
def main():
    model_size, input_list, output_path, sub_format, plus_time = get_commands(sys.argv)

    print(model_size, input_list, output_path, sub_format, plus_time)
    
if __name__ == '__main__':
    main()