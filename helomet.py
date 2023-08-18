import cv2
import numpy as np
import time
from playsound import playsound 
import requests
import schedule


net = cv2.dnn.readNet("yolov3-tiny-helm_final.weights", "yolov3-tiny-helm.cfg")
classes = []
with open("helm.names","r") as f:
    classes = [line.strip() for line in f.readlines()]

url = 'http://103.181.143.194:2002/hellomet'
urltime = "https://timeapi.io/api/TimeZone/zone?timeZone=Asia/Jakarta"

print(classes)
layer_names = net.getLayerNames()
outputlayers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

colors= np.random.uniform(0,255,size=(len(classes),3))

cap=cv2.VideoCapture(0)
# cap=cv2.VideoCapture('video1.mp4')

font = cv2.FONT_HERSHEY_SIMPLEX
starting_time= time.time()
frame_id = 0

count = 0
start = time.time()
def conect():
    try :
        r = requests.get(url,timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def sendDashboard(myobj):
    x = requests.post(url, myobj)
    print(x)

            

while True:
    _,frame= cap.read() # 
    frame_id+=1
    
    height,width,channels = frame.shape
    #detecting objects
    blob = cv2.dnn.blobFromImage(frame,0.00392,(320,320),(0,0,0),True,crop=False) #reduce 416 to 320    

        
    net.setInput(blob)
    outs = net.forward(outputlayers)
    #print(outs[1])


    #Showing info on screen/ get confidence score of algorithm in detecting an object in blob
    class_ids=[]
    confidences=[]
    boxes=[]
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if class_id == 0 and confidence > 0.5:
            # if confidence > 0.9:
                #onject detected
                center_x= int(detection[0]*width) #ymin
                center_y= int(detection[1]*height) #xmin
                w = int(detection[2]*width) #ymax
                h = int(detection[3]*height) #xmax

                #cv2.circle(img,(center_x,center_y),10,(0,255,0),2)
                #rectangle co-ordinat5s
                x=int(center_x - w/2)
                y=int(center_y - h/2)
                #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

                boxes.append([x,y,w,h]) #put all rectangle areas
                confidences.append(float(confidence)) #how confidence was that object detected and show that percentage
                class_ids.append(class_id) #name of the object tha was detect5
            elif class_id == 1 and confidence > 0.8:
            # if confidence > 0.9:
                #onject detected
                center_x= int(detection[0]*width) #ymin
                center_y= int(detection[1]*height) #xmin
                w = int(detection[2]*width) #ymax
                h = int(detection[3]*height) #xmax

                #cv2.circle(img,(center_x,center_y),10,(0,255,0),2)
                #rectangle co-ordinat5s
                x=int(center_x - w/2)
                y=int(center_y - h/2)
                #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

                boxes.append([x,y,w,h]) #put all rectangle areas
                confidences.append(float(confidence)) #how confidence was that object detected and show that percentage
                class_ids.append(class_id) #name of the object tha was detect5

    indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.4,0.6)


    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence= confidences[i]
            # color = colors[class_ids[i]]
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            # print(label)
            unique, counts = np.unique(class_ids, return_counts=True)
            tambah=0
            tambih=0
            # for i in range (len(counts)):
            #         cv2.putText(frame,label+" = "+str(counts[i]), (5,15+tambah),font,1, (0,0,255), 1)
            #         tambah=tambah+15
            wearing = 0
            notWearing = 0


            if label == 'Wearing Helmet':
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0, 200, 0),2)
                cv2.rectangle(frame, (x, y-labelSize[1]-10), (x+labelSize[0]+10, y+baseLine-10), (0, 200, 0), cv2.FILLED)
                cv2.putText(frame,label+" "+str(round(confidence,2)*100)+"%",(x,y-10),font,0.5,(255,255,255),2)
                for i in range (len(counts)):
                    cv2.putText(frame,label+" = "+str(counts[i]), (2,15+tambah),cv2.FONT_HERSHEY_PLAIN,1, (0,200,0), 2)
                    tambah=tambah+15
                    wearing = wearing + counts[i]

            if label == 'No Wearing Helmet':
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0, 0, 200),2)
                cv2.rectangle(frame, (x, y-labelSize[1]-10), (x+labelSize[0], y+baseLine-10), (0, 0, 200), cv2.FILLED)
                cv2.putText(frame,label+" "+str(round(confidence,2)*100)+"%",(x,y-10),font,0.5,(255,255,255),2)
                for i in range (len(counts)):
                    cv2.putText(frame,label+" = "+str(counts[i]), (2,35+tambih),cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 2)
                    tambah=tambih+25
                    notWearing = wearing + counts[i]
                    
            

                    # playsound('output3.mp3')
                    # time.sleep(5)
           
    #         schedule.every(1).minutes.do(sendDashboard, myobj)

            
    # schedule.run_pending()
    # time.sleep(1)
    run = time.time()        
    cv2.imshow("HELOMET",frame)
    if int(run - start) == 5:
        con = conect()
        if con == True :
            wc = requests.get(urltime)
            wib = wc.json()
            wib = wib["currentLocalTime"]
            tanggal = wib[:10]
            waktos = wib[11:19]
            myobj = {
                "pakai_helm" : wearing,
                "tidak_pakai" : notWearing,
                "tanggal": tanggal,
                "waktu" : waktos

            }
            x = requests.post(url, myobj)
            start = time.time()
            print(x.text)
        else :
            print ('koneksi tidak tersedia')


    count+=1

    key = cv2.waitKey(1) #wait 1ms the loop will start again and we will process the next frame
    
    if key == 27: #esc key stops the process
        break;
    
cap.release()    
cv2.destroyAllWindows()