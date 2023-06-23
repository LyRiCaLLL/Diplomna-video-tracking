import socket
import cv2
import numpy as np
import sys
import struct
import pickle
import time
import math
host = socket.gethostname()
port = 5000  # initiate port no above 1024
print(host)
c = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn,addr = s.accept()
    with conn:
        
        # Load Yolo
        print("LOADING YOLO")
        net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
        #save all the names in file o the list classes
        classes = []
        with open("coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        #get layers of the network
        layer_names = net.getLayerNames()
        #Determine the output layer names from the YOLO model 
        outputlayers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

        print("YOLO LOADED")



        video_capture = cv2.VideoCapture(0)


        while True:
            # Capture frame-by-frame
            re,img = video_capture.read()
            img = cv2.resize(img, None, fx=0.6, fy=0.6)
            height, width, channels = img.shape

            print(img.shape)

            # USing blob function of opencv to preprocess image
            blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
            #Detecting objects
            net.setInput(blob)
            outs = net.forward(outputlayers)

            # Showing informations on the screen
            class_ids = [] 
            confidences = []
            con = 0
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    # if confidence > 0.6 and classes[class_id] == 'person':
                    # if confidence > 0.6:
                    if confidence > 0.6 and class_id == 0:
                     # Object detected
                        con = confidence
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        


                        if len(boxes) == 0:
                            time.sleep(0.03)
                            bytes_val = center_x.to_bytes(math.ceil(center_x/255),'little')
                            conn.sendall(bytes_val)
                            bytes_val1 = center_y.to_bytes(math.ceil(center_y/255),'little')
                            conn.sendall(bytes_val1)
                            bytes_val2 = w.to_bytes(math.ceil(w/255),'little')
                            conn.sendall(bytes_val2)
                            bytes_val3 = h.to_bytes(math.ceil(h/255),'little')
                            conn.sendall(bytes_val3)
                            # print(h)
                            boxes.append([x, y, w, h])
                           
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
                            


                        

            #We use NMS function in opencv to perform Non-maximum Suppression
            #we give it score threshold and nms threshold as arguments.
        
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            font = cv2.FONT_HERSHEY_PLAIN
            # colors = np.random.uniform(0, 255, size=(len(classes), 3))
            colors = [(255, 0, 128)] * len(classes)
            
            for i in range(len(boxes)):
                
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[class_ids[i]]
                    
                    # cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 128), 1)
                    lineWidth = 30
                    #gorni lini
                    cv2.line(img, (x, y), (x+lineWidth , y),color,thickness=3)

                    cv2.line(img, (x, y), (x,y + lineWidth ),color,thickness=3)

                    cv2.line(img, (x + w, y ), (x+ w -lineWidth , y),color,thickness=3)

                    cv2.line(img, (x + w, y), (x + w,y + lineWidth ),color,thickness=3)
                    # долните лини 
                    cv2.line(img, (x, y + h), (x+lineWidth , y+h),color,thickness=3)

                    cv2.line(img, (x, y + h), (x,y + h - lineWidth ),color,thickness=3)

                    cv2.line(img, (x + w, y+h ), (x+ w -lineWidth , y+h),color,thickness=3)

                    cv2.line(img, (x + w, y+h), (x + w,y +h - lineWidth ),color,thickness=3)

                    cx = x+w //2
                    cy = y+h //2
                    area = w*h
                    # po tova she se vliae drona 

                    cv2.circle(img,(cx,cy),5,(0, 255, 0),cv2.FILLED) #tochkata v sredata na box 
                    # displayText = "{}:{:.4f}".format(label,confidence)

                    accuracy = h / w
                    displayText = "{}:{:.4f}".format(label,con)
                    # cv2.putText(img, f"Person: {accuracy:.2f}", (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX,1,color,2)

                    cv2.putText(img, displayText,(x, y - 10),cv2.FONT_HERSHEY_SIMPLEX,1,color,2)
                    # cv2.putText(img, label, (x, y - 10), font, 2, color, 2)
                    
            cv2.imshow("hackaton",cv2.resize(img, (800,600)))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        video_capture.release()
        cv2.destroyAllWindows()