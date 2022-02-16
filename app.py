#importing required files
from flask import Flask, render_template, Response, request
import cv2
from gaze_tracking import GazeTracking
from deepface import DeepFace


#declaration of variables
global capture, switch,execution ,frame_cnt,smile_count,pale_count,worried_count,anxious_count,surprise_count,angry_count,blink_cnt,other_count
global smilenormal_threshold , worriedanxioussurprise_threshold, angry_threshold, other_threshold,a,b
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


#Load pretrained face detection model    
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gaze = GazeTracking()
#instatiate flask app  
app = Flask(__name__, static_url_path='',static_folder='./static',template_folder='./templates')

#initializing camera setup
camera = cv2.VideoCapture(0)
camera.release()
cv2.destroyAllWindows()


# main function defination for detection of face and outcome   
# generate frame by frame from camera
def gen_frames(List):
        
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
                break
        #after camera is turned off switch = 0    
        if(switch==0):
            cal(frame_cnt)
            eyecal(List)
                    

#rendering to home page             
@app.route('/')
def normal():
    return render_template('normal.html')

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


#request routing from form in index.html
@app.route('/requests',methods=['POST','GET'])
def tasks():
    global execution
    if (execution == 0):
        execution = 1
    else :
        execution = 0   

    global switch,camera
    
    if request.method == 'POST':
       
        if  request.form.get('stop') == 'Stop/Start': 
            
            if(switch==1):
                switch=0
                camera = cv2.VideoCapture(0)
                

            else:
                camera.release()
                cv2.destroyAllWindows()
                switch=1
                
     
    elif request.method=='GET':
        return render_template('index.html')   
    if(execution == 1):
        return render_template('index.html')
    else :
        #returning values to home page to use in script for printing     
        return render_template('normal.html',data = frame_cnt , data1 = smile_count ,data2 = pale_count, data3 = worried_count,data4 = anxious_count,data5 = surprise_count,data6 = angry_count,data7 = blink_cnt,data8 = other_count ,var1 = smilenormal_threshold,var2 = worriedanxioussurprise_threshold ,var3 = angry_threshold,var4 = other_threshold ,eye = movement)

#yet to debug 
@app.route('/refresh')
def refresh():
    gen_frames(List)
    print("frame count at refresh-----",frame_cnt)
    return render_template('normal.html',data = frame_cnt)

#main     
if __name__ == '__main__':
    app.run()
    
    