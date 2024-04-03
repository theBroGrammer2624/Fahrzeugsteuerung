from tkinter import ttk
from tkinter import *
import RPi.GPIO as GPIO
import pigpio

import Datenbank
from Datenbank import auslesen

from picamera2 import Picamera2, Preview
from libcamera import Transform
from PIL import ImageTk
from PIL import Image as i # Für die Bildumwandlung von jpg in gif

from Ultrasonic import *
from servo import *
from Motor import *

from datetime import datetime
import time

import sys
import threading
import os

import line_trackingFreenove
lineTracking=line_trackingFreenove.Line_Tracking()
lnTrckgRunning = False

fenster = Tk()
fenster.title("RPi Fahrzeug")
fenster.geometry("1350x900")

# Globale Variablen
drive2nextObjRunning = False
threadSleep = False
servoWinkel = 75
servoBeißzange = 88
PWM=Motor()
servo=Servo()


"""
██████  ██ ███████ ████████  █████  ███    ██ ███████     ███████  ██████  ████████  ██████  
██   ██ ██ ██         ██    ██   ██ ████   ██    ███      ██      ██    ██    ██    ██    ██ 
██   ██ ██ ███████    ██    ███████ ██ ██  ██   ███       █████   ██    ██    ██    ██    ██ 
██   ██ ██      ██    ██    ██   ██ ██  ██ ██  ███        ██      ██    ██    ██    ██    ██ 
██████  ██ ███████    ██    ██   ██ ██   ████ ███████     ██       ██████     ██     ██████                                                                                               
"""
def distanzFoto(): # Distanz+Foto
        global bild
        global threadSleep #Stop barUpdateLoop Thread
        threadSleep = True
        time.sleep(0.025) #wait for barUpdate to finish

        # Distanzmessung
        ultrasonic=Ultrasonic()   
        data=ultrasonic.get_distance()   #Get the value
        data = round(data, 2)

        # Aktuelle Zeit abrufen
        aktuelle_zeit = datetime.now()
        # Stunden und Minuten extrahieren
        stunden = aktuelle_zeit.hour
        minuten = aktuelle_zeit.minute
        sekunde = aktuelle_zeit.second

        # Ausgabe der aktuellen Zeit
        zeit = f"{stunden:02d}:{minuten:02d}:{sekunde:02d} - "
        ausgabe.insert(END, zeit + str(data) + "cm\n")
        ausgabe.see("end")  # Automatisch nach unten scrollen

        # Camera logic
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration(main={"size": (640, 480)},transform=Transform(hflip=1,vflip=1))
        picam2.configure(preview_config)
        # Set white balance to "greyworld"
        picam2.awb_mode = 'greyworld'
        # picam2.start_preview(Preview.QTGL)
        picam2.start()
        metadata = picam2.capture_file("captured_image.jpg")
        print(metadata)
        picam2.close()

        # Convert the captured image to GIF using Pillow
        image = i.open("captured_image.jpg")
        image.save("captured_image.gif", format="gif")


        bild = PhotoImage(file="captured_image.gif")
        labelbild = Label(fenster, image=bild)
        labelbild.place(x=700, y=300, width=640, height=480)

        #delete created images
        os.remove("./captured_image.jpg")
        time.sleep(0.005)
        os.remove("./captured_image.gif")
        time.sleep(0.005)

        #SQL Distanz speichern
        Datenbank.init_db()
        Datenbank.speichern(data)
        #Datenbank.auslesen()

        threadSleep = False     # Start barUpdateLoop Thread

def clear():
        global bild
        bild = PhotoImage(file="./htl.GIF")
        labelbild = Label(fenster, image=bild)
        labelbild.place_forget()
        ausgabe.delete(1.0,END)


"""
██████  ██████  ██ ██    ██ ███████     ██████      ███    ██ ███████ ██   ██ ████████      ██████  ██████       ██ ███████  ██████ ████████ 
██   ██ ██   ██ ██ ██    ██ ██               ██     ████   ██ ██       ██ ██     ██        ██    ██ ██   ██      ██ ██      ██         ██    
██   ██ ██████  ██ ██    ██ █████        █████      ██ ██  ██ █████     ███      ██        ██    ██ ██████       ██ █████   ██         ██    
██   ██ ██   ██ ██  ██  ██  ██          ██          ██  ██ ██ ██       ██ ██     ██        ██    ██ ██   ██ ██   ██ ██      ██         ██    
██████  ██   ██ ██   ████   ███████     ███████     ██   ████ ███████ ██   ██    ██         ██████  ██████   █████  ███████  ██████    ██    
"""


def drive2nextObj():
    global drive2nextObjRunning
    ultrasonic=Ultrasonic()  #Ultrasonic Objekt erstellen
    if drive2nextObjRunning == True:
        
        distance = round(ultrasonic.get_distance(), 2) #Distanz auslesen
        bar["value"] = clamp((distance*2)-30, 0, 100) #bar updaten
        #time.sleep(0.01)
        print('**drive2nextObj mit', distance, 'cm Distanz**')

        if distance > 20:
            PWM.setMotorModel(2000, 2000) #Vorwaerts
            #time.sleep(0.01)
        else:
            PWM.setMotorModel(0, 0) #Motor stop
            drive2nextObjStop()

        fenster.after(50, drive2nextObj) #Wiederholen
    else:
        distance = round(ultrasonic.get_distance(), 2) #Distanz auslesen
        bar["value"] = clamp((distance*2)-30, 0, 100) #bar updaten
        #time.sleep(0.01)
        print('**drive2nextObj ENDE mit', distance, 'cm Distanz**')
        global threadSleep # Start barUpdateLoop Thread
        threadSleep = False

def drive2nextObjStart():
    global drive2nextObjRunning
    drive2nextObjRunning = True
    global threadSleep #Stop barUpdateLoop Thread
    threadSleep = True
    time.sleep(0.2)
    drive2nextObj()

def drive2nextObjStop():
    global drive2nextObjRunning
    drive2nextObjRunning = False



"""
██      ██ ███    ██ ███████     ████████ ██████   █████   ██████ ██   ██ ██ ███    ██  ██████  
██      ██ ████   ██ ██             ██    ██   ██ ██   ██ ██      ██  ██  ██ ████   ██ ██       
██      ██ ██ ██  ██ █████          ██    ██████  ███████ ██      █████   ██ ██ ██  ██ ██   ███ 
██      ██ ██  ██ ██ ██             ██    ██   ██ ██   ██ ██      ██  ██  ██ ██  ██ ██ ██    ██ 
███████ ██ ██   ████ ███████        ██    ██   ██ ██   ██  ██████ ██   ██ ██ ██   ████  ██████   
"""
def doAfterLine_Tracking():
    global lnTrckgRunning
    if lnTrckgRunning:
        lineTracking.doing()
        fenster.after(25, doAfterLine_Tracking)
    else:
        print('**Line Tracking finished**')
        PWM.setMotorModel(0,0)

def startLineTracking():
    global lnTrckgRunning
    if lnTrckgRunning == False:
        lnTrckgRunning = True
        print('**Line Tracking started**')
        PWM.setMotorModel(2000,2000)
        doAfterLine_Tracking()
    else:
        print('**Line Tracking is already running!**')

def stopLineTracking():
    global lnTrckgRunning
    lnTrckgRunning = False

"""
████████  █████  ███████ ████████  █████  ████████ ██    ██ ██████  ███████ ████████ ███████ ██    ██ ███████ ██████  ██    ██ ███    ██  ██████  
   ██    ██   ██ ██         ██    ██   ██    ██    ██    ██ ██   ██ ██         ██    ██      ██    ██ ██      ██   ██ ██    ██ ████   ██ ██       
   ██    ███████ ███████    ██    ███████    ██    ██    ██ ██████  ███████    ██    █████   ██    ██ █████   ██████  ██    ██ ██ ██  ██ ██   ███ 
   ██    ██   ██      ██    ██    ██   ██    ██    ██    ██ ██   ██      ██    ██    ██      ██    ██ ██      ██   ██ ██    ██ ██  ██ ██ ██    ██ 
   ██    ██   ██ ███████    ██    ██   ██    ██     ██████  ██   ██ ███████    ██    ███████  ██████  ███████ ██   ██  ██████  ██   ████  ██████  
"""
# Funktionen f�r Tastatursteuerung
def key_pressed(event): #Wird mehrmals aufgerufen wenn eine Taste gedrückt ist
    global servoWinkel
    global servoBeißzange
    key = event.char.lower()
    if key == 'w':
        PWM.setMotorModel(3000, 3000)  # Vorw�rts
        time.sleep(0.001)
    elif key == 's':
        PWM.setMotorModel(-3000, -3000)  # R�ckw�rts
        time.sleep(0.001)
    elif key == 'a':
        PWM.setMotorModel(-3000, 3000)  # Links
        time.sleep(0.001)
    elif key == 'd':
        PWM.setMotorModel(3000, -3000)  # Rechts
        time.sleep(0.001)
    # Servo Tastatursteuerung
    if key == 'r':
        servoWinkel += 1
        if servoWinkel > 140:
            servoWinkel = 140
        servo.setServoPwm('0',servoWinkel)  # nach oben

        time.sleep(0.01)
    elif key == 'f':
        servoWinkel -= 1
        if servoWinkel < 75:
            servoWinkel = 75
        servo.setServoPwm('0',servoWinkel)  # nach unten
        
        time.sleep(0.02)
    elif key == 'g':
        servoBeißzange += 6
        if servoBeißzange > 208:
            servoBeißzange = 208
        servo.setServoPwm('1',servoBeißzange) #Beißzange zu
        #print('ServoWinkel:', servoBeißzange)
        time.sleep(0.01)
    elif key == 't':
        servoBeißzange -= 6
        if servoBeißzange < 88:
            servoBeißzange = 88
        servo.setServoPwm('1',servoBeißzange) # Beißzange auf
        #print('ServoWinkel:', servoBeißzange)
        time.sleep(0.01)


def key_released(event): #Wird mehrmals aufgerufen wenn eine Taste gedrückt ist
    if lnTrckgRunning == False:
        PWM.setMotorModel(0, 0)  # Motor stoppen
        #print('Motor gestoppt')

# Tastatur-Eingabe abfangen
fenster.bind('<KeyPress>', key_pressed)
fenster.bind('<KeyRelease>', key_released)


"""
██████  ██████   ██████   ██████  ██████   █████  ███    ███ ███    ███ ███████ ████████  █████  ██████  ████████     ██ ███████ ███    ██ ██████  ███████ 
██   ██ ██   ██ ██    ██ ██       ██   ██ ██   ██ ████  ████ ████  ████ ██         ██    ██   ██ ██   ██    ██       ██  ██      ████   ██ ██   ██ ██      
██████  ██████  ██    ██ ██   ███ ██████  ███████ ██ ████ ██ ██ ████ ██ ███████    ██    ███████ ██████     ██      ██   █████   ██ ██  ██ ██   ██ █████   
██      ██   ██ ██    ██ ██    ██ ██   ██ ██   ██ ██  ██  ██ ██  ██  ██      ██    ██    ██   ██ ██   ██    ██     ██    ██      ██  ██ ██ ██   ██ ██      
██      ██   ██  ██████   ██████  ██   ██ ██   ██ ██      ██ ██      ██ ███████    ██    ██   ██ ██   ██    ██    ██     ███████ ██   ████ ██████  ███████ 
"""

def programm_ende():
    servo=Servo()
    global servoWinkel
    PWM.setMotorModel(0, 0)  # Motor stoppen
    for servoWinkel in range(servoWinkel, 75, -1):
        servo.setServoPwm('0',servoWinkel)
        time.sleep(0.01)
    servo.PwmServo.set_PWM_dutycycle(servo.channel1,0)
    servo.PwmServo.set_PWM_dutycycle(servo.channel2,0)
    servo.PwmServo.set_PWM_dutycycle(servo.channel3,0)
    #servo.setServoPwm('0',150)
    #servo.setServoPwm('1',90)
    print("Ende des Programms")
    fenster.destroy
    sys.exit()


def programmstart():
    print('''                                                                                                                                                      
     @&&@@@&&&%#*,          @@@@@@&%%&((@,,*#/                                                                                                        
     @@&@@&&&@&....         @@@@@@@&&&@&&#.,*#@#                                                                                                      
     @&&&@&&&&@@@@@&%      ,@@@@@@@&&&@@&&(/@@@&&@                                                                                                    
     @&&&@@&&&&@@@@@&&@    @@@@@@@@&&&@@@&&&&&&&&&@@/#&* ./&%(.                                                                                       
     %@%@@@@&@&@&@&&&%(*,*@@@@@@@&@&&&&@&@ %%%&&&&&&&&           ,%                                                                                   
   *%,&(&&&, /&&&&%%&&&&@@@@@(*.(%@&&&/@&&** #%%&&&&&&&&.            %                                                                                
    &&@&&&&( @&@@@@@@@@@@@@@@@%#@@@&&&&&&&     .%%&&&&&&&&,           #                                                                               
    @@@&&&&&&&&@@@@@@@@@@@@@@@@@@@@&&&&&&&        &&%&&&&&&@/          %                                                                              
    @&&@&&&**.&@@@@&@@@@@@@@@@@@@@@&&&@&&&@&        &%#&&&&&&&%        (,                                                                             
    @@@&&&*,/,,&@@@@@@@@( @@@@@@@@@&&&@&, ***(/       /%%&&&&&&&&      #.                                                                             
     ,#%%&@ .,.@@@@&&&@@@@@@@@@@@@@&&@&&%.**/#%%&        %&%%%%%%%&   *#   ,&&@((%(,,*/((/   ....     .((*                                            
      &&*&&&@@@@@@@@@@@@&@@@@@@* ##&&&&%%%%%%%%%%%%.       &%%%%%%%%% (%%@#.&.(%*      ,,/#%...      ./(//                                            
     %&/#%%&% @@@@@@@@@&@&&@       %%&%%%&%%%%%%%%%%%%       &%%%%%%%%%&.(      *          . .   .   (/#/%,                                           
   (&&&@@%%%%   @@@@@@@@@@@@@@/       %&%%%%&%%%%%%%%%%%      //%%%%%%%%%,    ,&&&&       ..........&/,.........,                                     
 ,&&&&&@&&&&&    /&@@&&&@@@@@@@@@       @&%&@@@%%%%%%%%%%%/ /     &&%%%%%%%%%. &@@#      ..........//..,*(/    .((                                    
 @&@&&&&&&&&    ,&@@@&&&&&&&@@@@@@@&       &@@&&%.#%%%%%%%%%&       @&%%%%&,####&@@,,//*,,,.......(.@@(((//%%&**,//%*.                                
 ,*@&&&&&&&&    &&&&&&&&&@&&&#&@@@@@@@.      *&&@@&@%%%%%%%%%%%&%&&&&&&&%%..,*%%&%&&&&**,,,..,,,,@@@&&%#((/*,,/#&//**                                 
 &@&&&&&&&&@     &@&&&&&&&&&&///#@@@@@@@@     @@&&&@@@@%%%%%%%%&&&@&&&&%&%&%%%&&&@@@%/**,,,,,*,##%@@@#&&&&#@@@@%@/***                                 
 &@&&&&&&&&&*(    # &&&&&&&&&@    %%@@@@@@@#  %@@@@@@&%%&%%%%%%&%&%%&&&&&&&&&&&&&@@%#/**,,,***&%#&@@@@@@&&@@@@@@@%(##       &@@&&%&&&&&(              
 /#&&&&&&&&&      @@@&&@&&@@&&&&##//&&&@@@@@@@/@@&&@@@%%%%%&%%&&&&&&&&&&&&&&&&&&&%%%#(******%#%&@@@@@@@@@@@%&&&(#####/#/@@@@&(@@%&,(,,*@@&@%/,%@@%%,  
 &&&&&&&&&&&,     %@@@&&&&&&&&&&&&@@/#/#&@@@@@@&&&&.,..   *#&&&&&&&&&&&&&@@@@@@@@#%%#((*//*@@%%&&&@@&&%&%%&%%@@((((((*&%.,.(#*,,/%@%/.*@@%/%@&@%@@&@. 
 &&@&&&&&&&%      #@@&&&&&&&&&&&&###(@#@@@@@@@&@&#*...,,...&(@@@&&&@@@@@@@@@@@@@@%##%##(/@@@&##%&@@@@@@@@@@&@@@@%((/,@&##&@@@%,&(,@@(&@#&@&@#/(**/(%( 
   @@(          &&&%,&&&&&&&&&&@&&@(@@&@@@@@@@@@@@@@@@@@@@@@@@@@&&,,@@@@@@&( &@@@#%#%%#@@@@@@@@@@@@@@@@@@@&%#((/&%/#(#/@&//@&@@%@/&@(&%@,@@@#******#&%
              ..((&@@@&&&&&&&&&@@@@&#@@@@@@@@@@@@@&%&@&@&@@@@@@@@  .(@@@@#.*,@@@@&%&&&&@@@@@@%((/#&(###@@%%@&%#*@@,.*,(@,&@/@@%@%@#@@@@@@@@.,**////&, 
              %&%@*&&&&&&&&&%%%&%@&%@@@@@@@*#@@@@@&%%&&@&%@@@@%*%@&&&&@%@@@&@@@@@%&&&&&&#@&///,#&(#%&%&@@@@@@@@@@@@@#@ @#@/&(@,@@@@@@@@@@@&@*/,*///&  
             ,%&&@@&&%&&&&&%@%&&@&@@@@@@@ &(*/%%@@%%/,*%#/%&@@@@((,/,@@@@@@@@@@@@&&&&&&&(%/&&@&*@@&%&@@@@@@&(@&(,*&./,,*,@/@@@@@@@@@@@@@@@,*,&#*///&&(
              .&&%&@%&#&%%%%&&&&&&@@@@@@@.%%%%&%@@@#%(((##%%@@@@&@@@&@@@&  @@@@@@&&&@@@@@@@&*/////,*((%((/%((@#&@ #%%*,(.* @@@@@@@@@@@@@@@,,*(%(//**  
              ,&#%@&@@@ &&@&*&&%@@@@@@@@%.%/%%%%#%&@@%@&(%#%%%%%&&&&%&&&&&&&&&&&&@@@@(&#/#%@@&&&&&&&&@@&&@@@@@&&&%,#&&@&*&,,@@@@@@@@@@@@@@/***(///@@& 
                &&&@%@&&###&@@@&@&@@@@@@@*#..##(*%#%&@@%%%%%##%%#@@@@@&&%,.#%(/**,,,.@%%%%#%%##(#&@@&((#///#(*&.*,*%@&/ %,/#@@@@@@@@@@@@@@,//////@*   
                 #&#@#%@@@@@&&@&&&&@@@@@@.@&%* %%&&&&&&..*/((%,*#@@@@@&@&..#%/*,,,,.%%%&%%#%&@%%@&&@@@&######%&%*(//(@@&((%#&@@@@@@@@@@@@@@&(*/((*    
                   .%#&@@@@@%#*&&&@@@@@@@,&&@%% &%%&& &@&(&.#%%&&@@@@@@@&.,%#/,.**..@&&&#@@@&%%@@&%%%%@%%@%%@&&%#/@%/*@&&%%%@@@@@@@@@@@@@@@@*#@(&&,   
                            @##&@@@&@@@@@@ #&@@ %%&&& %&&(/% /##&@@@@@@@& ,(#(,,*,.&&%@&&@(&%&%%%&%%#&&@@##&@&&**@&@*/&&&%%%@@@@@@@@&@@@@@@@@@@&.     
                                   ,%@@@@@&%%&&%%%%&@% ,&&&#.(#&&&@@@@@%@.,%@%/*,,,.&&%&&((&%&&@&&@&&%&&&&&%&&#**@@@(&&@&(,,@@@@@@@@@@@@@@@%/         
                                             #&%%%%%,,@%&&&%%%%&&&@@@@@@@.,@@@&&&&&&%%%%&&%//&@@@@&&&&&@@@&@&*/#/,*/(&@&%%%&@@@@@@@@@@&@&,            
                                                 %&&&,@%%&&%&&&&&%&&&&&&&&&&&&&&&&&&@@&&&@&&&@&@&&&%%&%%&/ .,&%/(//@@&%*(( @@@@@@@@@&,                
                                                          .%*   .%%(,     ,          %%%%&%&@@@@@@@&&&@@@@&@&***&%@&(&%/,,@@@@@@%@                    
                                                                                      @&@@&@@@&@&&%%##%&%&@@@@%./@#@%#%/*@@&#@*                       
                                                                                        .@ &&%&&%%&%&&@%&@&&@%,(,///%*%@&@&                           
                                                                                                *&#&%&&@@%%%% @%*&*,/&&&                              
                                                                                                           ,#&%%%&@#                                  ''')
    print("Das Programm wurde gestartet!")
    servo=Servo()
    global servoWinkel
    for servoWinkel in range(75, 140):
        servo.setServoPwm('0',servoWinkel)
        #print('ServoWinkel:', servoWinkel)
        time.sleep(0.01)
    servo.setServoPwm('1',servoBeißzange) #Zu



"""
 ██████  ██    ██ ██ 
██       ██    ██ ██ 
██   ███ ██    ██ ██ 
██    ██ ██    ██ ██ 
 ██████   ██████  ██ 
"""

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def barUpdate():
    #startzeit = time.time()
    #70ms
    #barDistance22 = round(ultrasonic.get_distance(), 2)
    #time.sleep(0.01)
    barDistance = round(ultrasonic.get_distance(), 2)
    time.sleep(0.01)
    bar["value"] = clamp((barDistance*2)-30, 0, 100)
    time.sleep(0.001)
    #70ms
    #endzeit = time.time()
    #dauer = endzeit - startzeit
    #print('Dauer:', dauer)
        
def barUpdateLoop():
    while True:
        if threadSleep:
            time.sleep(0.5)
        else:
            barUpdate()


ausgabe = Text(fenster, height=3, width=25)
ausgabe.place(x=0, y=200)
ausgabe.config(font=("Arial", 30))

start = Button(fenster, text="Distanz+Foto",activebackground="green", command=distanzFoto)
start.place(x=20, y=130)
start.config(font=("Arial",30))

start = Button(fenster, text="Video",activebackground="green", command=distanzFoto)
start.place(x=20, y=400)
start.config(font=("Arial",30))

lineTrackingBtn = Button(fenster, text="Tracking Modus aktivieren",activebackground="green", command=startLineTracking)
lineTrackingBtn.place(x=20, y=500)
lineTrackingBtn.config(font=("Arial",30))

lineTrackingBtnDeaktivieren = Button(fenster, text="Tracking Modus deaktivieren",activebackground="red", command=stopLineTracking)
lineTrackingBtnDeaktivieren.place(x=20, y=570)
lineTrackingBtnDeaktivieren.config(font=("Arial",30))

clear = Button(fenster, text="CLEAR", activebackground="blue", command=clear)
clear.place(x=500, y=100)
clear.config(font=("Arial",30))

destr = Button(fenster, text="Programm schließen", activebackground="red", command=programm_ende)
destr.place(x=700, y=100)
destr.config(font=("Arial",30))

auslesen_button = Button(fenster, text="Daten Auslesen", command=auslesen)
auslesen_button.place(x=50, y=650)
auslesen_button.config(font=("Arial",30))
auslesen_button.pack()

htlBild = PhotoImage(file="htl.GIF")
htlLabelbild = Label(fenster, image=htlBild)
htlLabelbild.place(x=5, y=5, width=278, height=90)

drive2nextObjButton = Button(fenster, text="drive2nextObj",activebackground="green", command=drive2nextObjStart)
drive2nextObjButton.place(x=20, y=640)
drive2nextObjButton.config(font=("Arial",30))


bar = ttk.Progressbar(fenster, orient=VERTICAL, length=300, mode='indeterminate')
bar.place(x=600, y=400)



programmstart()


# Thread der im Hintergrund läuft
barUpdate_thread = threading.Thread(target=barUpdateLoop)
barUpdate_thread.daemon = True # Der Thread wird beendet, wenn das Hauptprogramm beendet wird
barUpdate_thread.start()


"""
drive2nextObj_thread = threading.Thread(target=drive2nextObjTHREAD)
drive2nextObj_thread.daemon = True # Der Thread wird beendet, wenn das Hauptprogramm beendet wird
drive2nextObj_thread.start()
"""

mainloop()





