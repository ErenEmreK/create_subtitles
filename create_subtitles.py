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
    #We add plus_time to the normal end time of an instance (if it exceeds to next subtitle we just use next ones limit as limit)
    for i in range(len(result['segments']) - 1):
        start_time = convert_time(result['segments'][i]['start'])
        end_time = convert_time(min(result['segments'][i+1]['start'], 
                                    (result['segments'][i]['end']) + plus_time))
        
        sub_item = pysrt.SubRipItem(start=start_time, 
                                    end=end_time, 
                                    text=result['segments'][i]['text'])
        subs.append(sub_item)
    #And we add last subtitle instance
    subs.append(pysrt.SubRipItem(start=convert_time(result['segments'][-1]['start']), 
                                    end=convert_time(result['segments'][-1]['end']), 
                                    text=result['segments'][-1]['text']))
    
    subs.save(output_file, encoding='utf-8')
    print(f'Subtitle file {output_file} is ready.')   

def subtitles_for_list(model, video_list, sub_dir, sub_extension='.srt', plus_time=0):
    file_count = len(video_list)
    done = 0
    print(f"Creating subtitles for {file_count} files. This may take a while...")
    for video_path in video_list:
        #We get result texts from whisper
        result = model.transcribe(video_path)
        #We set subtitle name same as video name
        sub_file = os.path.splitext(os.path.basename(video_path))[0] + sub_extension
        if sub_extension == '.srt':
            result_to_srt(result, sub_file, plus_time=plus_time)
            done += 1
            print(f"{done}/{file_count}")
        else:
            #TODO implement other subtitle formats
            print(f"Unable to create {sub_extension} files. ")
            break
          
def get_commands(sys_args):
    
    if len(sys_args) >= 2:
        
        if sys_args[1] == "-h":
            print("Usage: create_subtitles.py [path/to/input/file.mp4 OR path/to/input/folder] -o [path/to/output/folder] -f [subtitle format] -p [plus time] -m [model size]")
            #TODO be more verbose here
            sys.exit()
            
        output_dir = None
        plus_time = 0
        sub_format = '.srt'
        model_size = 'small'
        input_list = []
        
        extensions = ['.mp4', '.mkv', '.mp3', '.wav', '.mpeg', '.m4a', '.webm']
        sub_extensions = ['.srt']
        
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
            
        for n in range(len(sys_args)):
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
                    plus_time = float(sys_args[n + 1]) 
                except (ValueError, IndexError):
                    print("Plus-time didn't specified properly.")
                    sys.exit()
            
            if sys_args[n] == "-m":
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
        
            
        return model_size, input_list, output_dir, sub_format, plus_time
    
    else:
        print("You must enter an input path.")
        sys.exit()

    
def main():

    model_size, input_list, output_dir, sub_format, plus_time = get_commands(sys.argv)
   
    model = whisper.load_model(model_size)
    subtitles_for_list(model, input_list, output_dir, sub_format, plus_time)
    
    
if __name__ == '__main__':
    main()