
# Subtitle Creator

A command-line application to easily create subtitles for video/audio files using OpenAI's Whisper library.




## Dependencies

#### ffmpeg
Whisper uses the brilliant command-line tool [ffmpeg](https://ffmpeg.org/) in order to manipulate media files. You can install it via commands below in case you don't have already. Also keep in mind that you may need to add it to PATH afterwards.

```
# on Ubuntu
sudo apt update && sudo apt install ffmpeg

# on Windows using Chocolatey
choco install ffmpeg

# on MacOS using Homebrew 
brew install ffmpeg
```

#### Whisper
You can install our main Speech to Text model [whisper](https://github.com/openai/whisper) via:
```
pip install openai-whisper
```

#### pysrt

[Pysrt](https://github.com/byroot/pysrt) facilitates converting texts to srt files. Install with commands below:

```
pip install pysrt
```

## Usage

#### Important Update 1.01!!
After discovering wonderful Python library [stable-ts](https://github.com/jianfch/stable-ts) i did some updates in order to be able work with its improved model. So if you want to create efficient subtitles quickly using stable_whisper model, this is the way to go now:

```python
create_subtitles.py path/to/video.mp4 -s
                or
create_subtitles.py path/to/video/folder -s
```
And if you want to use timestamps for active words:
```python
create_subtitles.py path/to/video.mkv -s -t
```
You can still use offset -more information below about how offset works- in order subtitles to stay longer via -p command (only caveat being you can not use timestamps when you are using offset):
```python
create_subtitles.py path/to/video.mkv -s -p 0.75
```
You can use other commands too:
```python
create_subtitles.py path/to/video.mkv -o  path/to/subtitle/folder -s -p 0.5 -m base 
```
#### If you still prefer legacy version: 

Basic usage requires only a video/audio file to create subtitles for.
```python
create_subtitles.py path/to/video.mkv 
```
You can also just use a folder name instead, it will create subtitles for all available media files in that folder.
```python
create_subtitles.py path/to/video/directory
```
You can declare directory you want subtitles to be created in. (If you don't use -o arguement, it will save the subtitle files into the video directory by default.)
```python
create_subtitles.py path/to/video.mp4 -o path/to/subtitle/directory
```
-p arguement will add desired amount of (seconds) offset time to end of every subtitle instance. Since AI generated subtitle will exactly disappear when sentence is finished, it is recommended to use 0.5 to 1.5 second of offset. (If next subtitle instance comes too quickly it will keep the instance till the next one to ensure they won't crash.)
```python
create_subtitles.py path/to/video.mp4 -p 1
```
-m arguement will define the size of used speech to text model's size. It's set to 'small' by default. But whisper provides  quicker and less capable models along with slower and more complicated ones. You can see all parameters in [here](https://github.com/openai/whisper). 

Since bigger models consume considerably more VRAM, be sure your GPU is up to task before using those. You can also see the requirements in the link above.

```python
create_subtitles.py path/to/video/folder -p 0.75 -m small 
```
