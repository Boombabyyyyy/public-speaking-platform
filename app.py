#importing required files
mysp=__import__("my-voice-analysis") #???
from tkinter import messagebox
from flask import *  
from flask_cors import CORS, cross_origin
from distutils.log import debug
from flask import Flask, jsonify, render_template, Response, request
import cv2
from gaze_tracking import GazeTracking
from deepface import DeepFace
import json

#speech recognization import start
import speech_recognition as sr
import sounddevice as sd
import queue
import soundfile as sf
import threading
from tkinter import *

from flask import Flask, render_template, Response, request
from gingerit.gingerit import GingerIt
import language_tool_python
from gingerit.gingerit import GingerIt
import parselmouth
from parselmouth.praat import call, run_file #???

#speech import ends

#instatiate flask app
app = Flask(__name__, static_url_path='',static_folder='./static',template_folder='./templates')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


#declaration of variables
global capture, switch,execution ,frame_cnt,smile_count,pale_count,worried_count,anxious_count,surprise_count,angry_count,blink_cnt,other_count
global smilenormal_threshold , worriedanxioussurprise_threshold, angry_threshold, other_threshold,a,b, percent_smile
global goodblink , noblink ,moreblink, i, goodeye, badeye, videoerrm, c, artigood
#speech variable initialized
global recording,file_exists,exe,var,text,listing,grammermist,pauses,articulates,duration,rate_of_speech,ready
global matches, mistakes, crt_text, text_list, crt_text_list, crt_l, t_l, ros_mins, ros_perf, ros_slow, ros_fast, ros_error
capture=0
switch=1
execution = 0
frame_cnt = 1
smile_count = 0
percent_smile = 0
pale_count = 0
worried_count = 0
anxious_count = 0
surprise_count = 0
angry_count = 0
other_count = 0
blink_cnt = 0
smilenormal_threshold =0
worriedanxioussurprise_threshold = 0
angry_threshold = 0
other_threshold = 0
movement = 0
a=[]
b=[]
List = []

#speech variable initialized
ready = 1
exe = 0
text = []
listing = []
grammermist=0
pauses = 0
articulates = 0
duration = 0
rate_of_speech = 0
#end

#Load pretrained face detection model    
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gaze = GazeTracking()
 
#initializing camera setup
camera = cv2.VideoCapture('test.webm')

# main function defination for detection of face and outcome   
# generate frame by frame from camera
def gen_frames(List):
    
    print("----gen frame----")
    camera = cv2.VideoCapture('test.webm')
    global capture,frame_cnt,smile_count,pale_count,worried_count,anxious_count,surprise_count,angry_count,other_count
    frame_cnt = 1
    smile_count = 0
    pale_count = 0
    worried_count = 0
    anxious_count = 0
    surprise_count = 0
    angry_count = 0
    other_count = 0
    List = []
    
    # emotiones recognized by model
    emotions = ["happy", "sad", "neutral", "fear", "surprise", "disgust", "angry"]
    print("-----inside gen frame function-----")       
    # video capture and tracing   
    while True:
        #success true means camera is on
        
        success, frame = camera.read() 
        if not success:
            break
        else:
            frame_cnt = frame_cnt + 1 
            # We get a new frame from the webcam
            
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.1, 4)

            for(x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


            # logic for counting which emotion occured how many times
            final_emotion = result['dominant_emotion']
            if final_emotion == emotions[0]:
                smile_count = smile_count+1
            elif final_emotion == emotions[1]:
                worried_count = worried_count+1
            elif final_emotion == emotions[2]:
                pale_count = pale_count+1
            elif final_emotion == emotions[3]:
                anxious_count = anxious_count+1
            elif final_emotion == emotions[4]:
                surprise_count = surprise_count+1
            elif final_emotion == emotions[5]:
                other_count = other_count+1
            elif final_emotion == emotions[6]:
                angry_count = angry_count+1

            # part 2 -eye movement detection

            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)

            frame = gaze.annotated_frame()
            text = ""

            if gaze.is_blinking():
                text = "Blinking"
            elif gaze.is_right():
                text = "right"
            elif gaze.is_left():
                text = "left"  
            elif gaze.is_center():
                text = "center"


            if text == "left":
                List.append("l")
            if text == "right":
                List.append("r") 
            if text == "center":
                List.append("c")      

            
            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   

           
            
            #popupmsg("The processing of video is finished you can check the results now", "processing")
            #switch = 0
    print("frame count------------",frame_cnt)
    print( "Data: ")
    print(smile_count, worried_count, pale_count, anxious_count, surprise_count, other_count, angry_count)
    cal(frame_cnt)
    eyecal(List)
    camera.release()
    cv2.destroyAllWindows()

    
                    
   





#speech functions start
#pauses in speech
def mysppaus(m,p):
    sound=p+"/"+m+".wav"
    sourcerun=p+"/myspsolution.praat" #????
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[1]) # will be the integer number 10
        z4=float(z2[3]) # will be the floating point number 8.3
        
    except:
        z3=0
        print ("Try again the sound of the audio was not clear")
    return z3;

#articulation_rate
def myspatc(m,p):
    sound=p+"/"+m+".wav"
    sourcerun=p+"/myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[3]) # will be the integer number 10
        z4=float(z2[3]) # will be the floating point number 8.3
    except:
        z3=0
        print ("Try again the sound of the audio was not clear")
    return z3;# syllables/sec speaking duration

#pauses in speech
def myspod(m,p):
    sound=p+"/"+m+".wav"
    sourcerun=p+"/myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[3]) # will be the integer number 10
        z4=float(z2[5]) # will be the floating point number 8.3
        #print ("original_duration=",z4,"# sec total speaking duration with pauses")
    except:
        z4=0
        print ("Try again the sound of the audio was not clear")
    return z4 ;

#rate of speech
def myspsr(m,p):
    sound=p+"/"+m+".wav"
    sourcerun=p+"/myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[2]) # will be the integer number 10
        z4=float(z2[3]) # will be the floating point number 8.3
        #print ("rate_of_speech=",z3,"# syllables/sec original duration")
    except:
        z3=0
        print ("Try again the sound of the audio was not clear")
    return z3;
#speech functions end


#function for speech to text
def speechtotext():
    global text,grammermist,pauses,articulates,duration,rate_of_speech, matches, mistakes, crt_text, text_list, crt_text_list, crt_l, t_l, ros_perf, ros_slow, ros_fast, ros_mins, ros_error, artigood
    ros_perf=False
    ros_slow=False
    ros_fast=False
    artigood = False

    r = sr.Recognizer()

    file_audio = sr.AudioFile('audio.wav')

    with file_audio as source:
        audio_text = r.record(source)
    text = r.recognize_google(audio_text, language='en-IN')
    #corrected_text = GingerIt().parse(text)

     #grammer checking
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    #print(len(matches)) 
    grammermist=0
    while grammermist<len(matches):
        listing=matches[grammermist]
        #print(matches[grammermist])
        grammermist+=1
        
    len(matches)
    mistakes=[tool]
    crt_text=tool.correct(text)
    text_list=text.split()
    crt_text_list=crt_text.split()
    crt_l=[]
    t_l=[]
    for i in range(len(text_list)):
        if text_list[i]!=crt_text_list[i]:
            crt_l.append(crt_text_list[i])
    print(crt_l)
    for i in range(len(text_list)):
        if text_list[i]!=crt_text_list[i]:
            t_l.append(text_list[i])
    print(t_l)
    
    #code suggested
    p="audio" # Audio File title
    c=r"/mountdisk/PSnew" 
    pauses = mysppaus(p,c)
    articulates = myspatc(p,c)
    duration = myspod(p,c)
    rate_of_speech = myspsr(p,c)

    ros_mins = rate_of_speech*60

    if (rate_of_speech == 2 or rate_of_speech == 3):
        ros_perf = True
    
    elif (rate_of_speech < 2):
        ros_slow = True

    elif (rate_of_speech > 3):
        ros_fast = True
    
    else:
        ros_error = True

    if articulates >=4 and articulates <=5:
        artigood = True

    
        

    return grammermist,pauses,articulates,duration,rate_of_speech,text,ros_mins,ros_perf,ros_slow,ros_fast,ros_error


    
#rendering to home page             


@app.route('/')  
@cross_origin()
def upload():  
    return render_template('normal.html')


@app.route('/upload', methods = ['POST']) 
@cross_origin(origin='http://127.0.0.1:5500',headers=['Content- Type']) #update this link and find out what this does.
def uplload():  
    if request.method == 'POST':  
        f = request.files['file']
        f.save(f.filename)  
        return jsonify(success=True)        


@app.route("/audio", methods=["GET", "POST"])
def audios():
    if request.method == "POST":
        file = request.files['audio_data']
        with open('audio.wav', 'wb') as audio:
            file.save(audio)
        print('file uploaded successfully')
       
    return render_template('upload.html', request="POST")
    
        




@app.route('/uploading')
def uploading():
    return render_template('upload.html')

@app.route('/normal')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('normal.html')  

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/upload_old')
def upload_old():
    return render_template('upload_old.html')

#function for calculation of face expression
def cal(frame_cnt):
    global smilenormal_threshold , worriedanxioussurprise_threshold, angry_threshold, other_threshold,blink_cnt, percent_smile
    smilenormal_threshold =0
    worriedanxioussurprise_threshold = 0
    angry_threshold = 0
    other_threshold = 0
    smilenormal_threshold = frame_cnt/2
    worriedanxioussurprise_threshold = frame_cnt/3
    angry_threshold = frame_cnt/4
    other_threshold = frame_cnt/4
    blink_cnt = frame_cnt/22
    percent_smile = int((smile_count/frame_cnt)*100)

goodblink=False
noblink=False
moreblink=False
goodeye=False
badeye=False
videoerr=False
c=12
i=88

#function for calculation of eye movement
def eyecal(List):
    global blink_cnt,movement,a,b,goodblink,noblink,moreblink,goodeye,badeye,videoerr
    movement = 0
    blink_cnt = 0
    a=[]
    b=[]
    for k in range(1, len(List)):
    # Get two adjacent elements.
        a = List[k - 1]
        b = List[k]

        if a != b :
            movement = movement+1
    i=88
    while (i < frame_cnt):
        if (blink_cnt == frame_cnt/22):
            i = i * 2
            goodblink=True
            break
        elif (blink_cnt < frame_cnt/22):
            i = i * 2
            noblink=True
            break
        else:
            moreblink=True
            break
    c=12
    if (frame_cnt > 88):
        if (movement > frame_cnt/c):
            badeye = True
            c=c*i
        else:
            goodeye = True
    else:
        videoerr = True
    







    

#function to view video feed on screen
@app.route('/video_feed')
def video_feed():
        print("--------called video feed---------")
        return Response(gen_frames(List), mimetype='multipart/x-mixed-replace; boundary=frame')
    


#video and audio routing
@app.route('/requests',methods=['POST','GET'])
def tasks1():
    global switch,camera,ready
    
    if request.method == 'POST':
        if  request.form.get('stop') == 'Get Report': 
            #returning values to home page to use in script for printing  
            speechtotext()   
            return render_template('report.html',data = frame_cnt , data1 = smile_count ,data2 = pale_count, 
            data3 = worried_count,data4 = anxious_count,data5 = surprise_count,data6 = angry_count,
            data7 = blink_cnt,data8 = other_count ,var1 = smilenormal_threshold,var2 = worriedanxioussurprise_threshold ,
            var3 = angry_threshold,var4 = other_threshold ,eye = movement,transcript=text, gram = grammermist , 
            pau = pauses , arti = articulates , dur = duration , ros =rate_of_speech,
            sm = percent_smile, i = i, goodblink = goodblink, noblink = noblink, moreblink =moreblink, goodeye = goodeye,
            c=c, badeye=badeye, videoerr=videoerr, crt_text=crt_text, crt_l=crt_l, t_l=t_l, ros_mins=ros_mins,
            ros_perf=ros_perf,ros_slow=ros_slow,ros_fast=ros_fast,ros_error=ros_error, artigood=artigood)
    
         
#main
if __name__ == '__main__':
    # context = ('/etc/nginx/ssl/lightinfosys.crt', '/etc/nginx/ssl/lightinfosys.key')
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
    app.run(debug=True)




