"""
from fer import Video
from fer import FER
import pandas as pd

# Put in the location of the video file that has to be processed
location_videofile = "D:\CSE\E42\public-speaking-platform\Video_One.webm"

# But the Face detection detector
face_detector = FER(mtcnn=True)
# Input the video for processing
input_video = Video(location_videofile)

# The Analyze() function will run analysis on every frame of the input video. 
# It will create a rectangular box around every image and show the emotion values next to that.
# Finally, the method will publish a new video that will have a box around the face of the human with live emotion values.
processing_data = input_video.analyze(face_detector, display=False)

vid_df = input_video.to_pandas(processing_data)
vid_df = input_video.get_first_face(vid_df)
vid_df = input_video.get_emotions(vid_df)

angry = sum(vid_df.angry)
disgust = sum(vid_df.disgust)
fear = sum(vid_df.fear)
happy = sum(vid_df.happy)
sad = sum(vid_df.sad)
surprise = sum(vid_df.surprise)
neutral = sum(vid_df.neutral)

emotions_values = [angry, disgust, fear, happy, sad, surprise, neutral]

print(angry, disgust, fear, happy, sad, surprise, neutral)
"""
# smile_count = 300
# frame_cnt = 1288
# percent_smile = int((smile_count/frame_cnt)*100)
# print(percent_smile)

import language_tool_python
tool = language_tool_python.LanguageTool('en-US')
text = "I has lot's of apples"
matches = tool.check(text)
len(matches)
mistakes=[tool]
crt_text=tool.correct(text)
text_list=text.split()
crt_text_list=crt_text.split()
l=[]
for i in range(len(text_list)):
    if text_list[i]!=crt_text_list[i]:
        l.append(crt_text_list[i])
print(text)
print(crt_text)
print(text_list)
print(crt_text_list)
print(l)