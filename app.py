#importing required files
mysp=__import__("my-voice-analysis")
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
#import tkinter as tk
#from tkinter import Button, Tk, messagebox
#from tkinter import ttk
import queue
import soundfile as sf
import threading
from tkinter import *

from flask import Flask, render_template, Response, request
from gingerit.gingerit import GingerIt
import language_tool_python
from gingerit.gingerit import GingerIt
import parselmouth
from parselmouth.praat import call, run_file

#speech import ends

#instatiate flask app
app = Flask(__name__, static_url_path='',static_folder='./static',template_folder='./templates')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


#declaration of variables
global capture, switch,execution ,frame_cnt,smile_count,pale_count,worried_count,anxious_count,surprise_count,angry_count,blink_cnt,other_count
global smilenormal_threshold , worriedanxioussurprise_threshold, angry_threshold, other_threshold,a,b
#speech variable initialized
global recording,file_exists,exe,var,text,listing,grammermist,pauses,articulates,duration,rate_of_speech,ready
capture=0
switch=1
execution = 0
frame_cnt = 1
smile_count = 0
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
               
        # video capture and tracing   
        while True:
            #success true means camera is on
            
            success, frame = camera.read() 

            if success == True :
                #for determining threshold 
                
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
        
                ret,buffer = cv2.imencode('.jpg',frame)
                frame = buffer.tobytes()
                yield(b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                
            else:
                #popupmsg("The processing of video is finished you can check the results now", "processing")
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
                break
                      
        #after camera is turned off switch = 0    
        if(switch==0):
            cal(frame_cnt)
            eyecal(List)




def audio():
    
    #audio funtion here
    #Define the user interface
    voice_rec = Tk()
    voice_rec.geometry("175x100")
    voice_rec.title("Voice Recorder")
    voice_rec.config(bg="#107dc2")

    #Create a queue to contain the audio data
    q = queue.Queue()
    #Declare variables and initialise them
    recording = False
    file_exists = False    

    #Fit data into queue
    def callback(indata, frames, time, status):
        q.put(indata.copy())

    #Functions to play, stop and record audio
    #The recording is done as a thread to prevent it being the main process
    def threading_rec(x):
        if x == 1:
            #If recording is selected, then the thread is activated
            t1=threading.Thread(target= record_audio)
            t1.start()
        elif x == 2:
            #To stop, set the flag to false
            global recording
            recording = False
            messagebox.showinfo(message="Recording finished")
        elif x == 3:
            #To play a recording, it must exist.
            if file_exists:
                #Read the recording if it exists and play it
                data, fs = sf.read("trial.wav", dtype='float32') 
                sd.play(data,fs)
                sd.wait()
            else:
                #Display and error if none is found
                messagebox.showerror(message="Record something to play")

    #Recording function
    def record_audio():
        #Declare global variables    
        global recording 
        #Set to True to record
        recording= True   
        global file_exists 
        #Create a file to save the audio
        messagebox.showinfo(message="Recording Audio. Speak into the mic")
        with sf.SoundFile("trial.wav", mode='w', samplerate=44100,
                            channels=2) as file:
        #Create an input stream to record audio without a preset time
                with sd.InputStream(samplerate=44100, channels=2, callback=callback):
                    while recording == True:
                        #Set the variable to True to allow playing the audio later
                        file_exists =True
                        #write into file
                        file.write(q.get())

        
    #Label to display app title
    #title_lbl  = Label(voice_rec, text="Voice Recorder", bg="#107dc2").grid(row=0, column=0, columnspan=2)
    #Button to record audio
    record_btn = Button(voice_rec, text="Record Audio", command=lambda m=1:threading_rec(m))
    #Stop button
    stop_btn = Button(voice_rec, text="Stop Recording", command=lambda m=2:threading_rec(m))
    
    #Position buttons
    record_btn.grid(row=1,column=1)
    stop_btn.grid(row=1,column=2)
    voice_rec.mainloop()
    #audio function end


#speech functions start
#pauses in speech
def mysppaus(m,p):
    sound=p+"/"+m+".wav"
    sourcerun=p+"/myspsolution.praat"
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
    global text,grammermist,pauses,articulates,duration,rate_of_speech
    r = sr.Recognizer()

    file_audio = sr.AudioFile('trial.wav')

    with file_audio as source:
        audio_text = r.record(source)
    text = r.recognize_google(audio_text)
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
    
    
    #code suggested
    p="trial" # Audio File title
    c=r"D:\monami_project" 
    pauses = mysppaus(p,c)
    articulates = myspatc(p,c)
    duration = myspod(p,c)
    rate_of_speech = myspsr(p,c)
    return grammermist,pauses,articulates,duration,rate_of_speech

    
#rendering to home page             


@app.route('/')  
@cross_origin()
def upload():  
    return render_template('normal.html')


@app.route('/upload', methods = ['POST']) 
@cross_origin(origin='http://127.0.0.1:5500',headers=['Content- Type'])
def uplload():  
    if request.method == 'POST':  
        f = request.files['file']
        f.save(f.filename)  
        return jsonify(success=True)        

@app.route('/uploading')
def uploading():
    return render_template('upload.html')

@app.route('/normal')
def index():
    return render_template('index.html')    

#function for calculation of face expression
def cal(frame_cnt):
    global smilenormal_threshold , worriedanxioussurprise_threshold, angry_threshold, other_threshold,blink_cnt
    smilenormal_threshold =0
    worriedanxioussurprise_threshold = 0
    angry_threshold = 0
    other_threshold = 0
    smilenormal_threshold = frame_cnt/2
    worriedanxioussurprise_threshold = frame_cnt/3
    angry_threshold = frame_cnt/4
    other_threshold = frame_cnt/4
    blink_cnt = frame_cnt/22

#function for calculation of eye movement
def eyecal(List):
    global blink_cnt,movement,a,b
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
    

#function to view video feed on screen
@app.route('/video_feed')
def video_feed():
        return Response(gen_frames(List), mimetype='multipart/x-mixed-replace; boundary=frame')
    
#audio        
@app.route('/requests',methods=['POST','GET'])
def tasks():
    
        
    global switch,camera,ready
    
    if request.method == 'POST':
        
        if request.form.get('recordings') == 'Record Audio':
            if(ready==1):
                ready=0
                audio()
            else:
                speechtotext()
                ready=1

     
    elif request.method=='GET':
        return render_template('index.html')   
    if(execution == 1):
        return render_template('index.html')
    else :
        #returning values to home page to use in script for printing   
        return render_template('normal.html',data = frame_cnt , data1 = smile_count ,data2 = pale_count, data3 = worried_count,data4 = anxious_count,data5 = surprise_count,data6 = angry_count,data7 = blink_cnt,data8 = other_count ,var1 = smilenormal_threshold,var2 = worriedanxioussurprise_threshold ,var3 = angry_threshold,var4 = other_threshold ,eye = movement,input = text , gram = grammermist , pau = pauses , arti = articulates , dur = duration , ros =rate_of_speech)


#video routing
@app.route('/requests',methods=['POST','GET'])
def tasks1():
    global switch,camera,ready
    
    if request.method == 'POST':
        if  request.form.get('stop') == 'Get Report': 
            #returning values to home page to use in script for printing     
            return render_template('normal.html',data = frame_cnt , data1 = smile_count ,data2 = pale_count, data3 = worried_count,data4 = anxious_count,data5 = surprise_count,data6 = angry_count,data7 = blink_cnt,data8 = other_count ,var1 = smilenormal_threshold,var2 = worriedanxioussurprise_threshold ,var3 = angry_threshold,var4 = other_threshold ,eye = movement ,  data9 = text , data10 = grammermist , data12 = pauses , data13 = articulates)

        else:
            print("------in else part------------")    

#main     
if __name__ == '__main__':
    app.run(debug=True)



