import numpy as np
import imutils
import RPi.GPIO as GPIO
import cv2
import time, threading
import telegram        
avg = None
video = cv2.VideoCapture(0)
bot = telegram.Bot(token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX") #CameraTrapBot
chat_id = 781168949 #Zafier
pir = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir, GPIO.IN)

def find_majority(k):
    myMap = {}
    maximum = ( '', 0 ) # (occurring element, occurrences)
    for n in k:
        if n in myMap: myMap[n] += 1
        else: myMap[n] = 1

        # Keep track of maximum on the go
        if myMap[n] > maximum[1]: maximum = (n,myMap[n])
    return maximum

last = time.perf_counter()
current = last
while 1:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if avg is None:
        print ("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        continue
    current = time.perf_counter()
    cv2.accumulateWeighted(gray, avg, 0.5)  #Memperbarui rata-rata berjalan. Fungsi menghitung jumlah tertimbang dari gambar input src dan akumulator dst sehingga dst menjadi rata-rata berjalan dari urutan bingkai
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))  #Menghitung perbedaan absolut per-elemen antara dua array atau antara array dan skalar.  
    thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if GPIO.input(pir):
        if current - last > 5.:
            last = current
            cv2.imwrite('capture.jpg',frame)
            print('PIR Detek!-------------')
            print('Gambar Telah di Capture')
            bot.sendMessage(chat_id, str("Halo Eliza, PIR detection dari Sensor!"))
            bot.sendPhoto(chat_id = chat_id, photo=open('./capture.jpg', 'rb'))
            print('Notifikasi telah dikirim')            
    for c in cnts:
        if cv2.contourArea(c) < 5000:    
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 50, 25), 2)
        if current - last > 5.:
            last = current
            cv2.imwrite('capture.jpg',frame)
            print('Motion Detek!----------')
            print('Gambar Telah di Capture')
            bot.sendMessage(chat_id, str("Halo Eliza, Motion detection dari Kamera!"))
            bot.sendPhoto(chat_id = chat_id, photo=open('./capture.jpg', 'rb'))
            print('Notifikasi telah dikirim')

    cv2.imshow("Frame",frame)
##    cv2.imshow("Gray",gray)
##    cv2.imshow("FrameDelta",frameDelta)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
video.release()
cv2.destroyAllWindows()
