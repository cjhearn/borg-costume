################
# BORG COSTUME #
# Chris Hearn  #
# 2022         #
################

from machine import ADC, Pin, PWM, Timer
from time import sleep
import _thread
import random

# SETUP
# LEDs
brightLevel = 1 # 5 steps of 13005, default = 3 = 39015 = 60%
brightDuty = brightLevel * 13005
brightHalf = round(brightDuty / 2)
brightQtr = round(brightDuty / 4)
ledList = ["led1"]
led1 = PWM(Pin(25))
timLED = Timer()

# Battery
batteryFull = 4.28
batteryEmpty = 2.75
vsys = ADC(29)
batteryCharging = Pin(24, Pin.IN)
batteryCF = 3 * 3.3 / 65535

# Eyepiece LED circle 
eyeLock = _thread.allocate_lock()
circle = 1
runCircle = 1
spinMode = 1 # 1 = with fade, 2=no fade, 3=full on static, 4=off
c1 = PWM(Pin(21))
c2 = PWM(Pin(20))
c3 = PWM(Pin(19))
c4 = PWM(Pin(18))
cC = PWM(Pin(17))
c1.freq(1000)
c2.freq(1000)
c3.freq(1000)
c4.freq(1000)
cC.freq(1000)
timCircle = Timer()


# Servo
MIN = 450000
MID = 1500000
MAX = 1980000
servo = PWM(Pin(14))
servo.freq(50)
servo.duty_ns(MID)
servoLocked = 0
timServo = Timer()

# Ultrasonic Distance Sensor
trig = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN, Pin.PULL_DOWN)
timDistance = Timer()

# Button breakout board
rowList = [1,2,3]
colList = [4,5]

for x in range(0,2):
    rowList[x] = Pin(rowList[x], Pin.OUT)
    rowList[x].value(1)
    
for x in range(0,1):
    colList[x] = Pin(colList[x], Pin.IN, Pin.PULL_UP)

keyMap = [["6","5"],["4","3"],["2","1"]]

timButtons = Timer()

def buttonRead(cols,rows):
    pass
#    global brightLevel
#    for r in rows:
#        r.value(0)
#        result = [cols[0].value(), cols[1].value()]
#        
#    if min(result) == 0:
#        key = keyMap[int(rows.index(r))][int(result.index(0))]
#        r.value(1)
#        print("Button "+key+" pressed")
#        if key == "1": # Check battery level
#            time.sleep(0.2)
#            runCircle = 0
#            batteryCheck()
#        elif key == "2": # LED brightness
#            time.sleep(0.2)
#            brightLevel += 1
#            if brightLevel > 5:
#                brightLevel = 1
#                
#        elif key == "3": # eyepiece spin mode
#            time.sleep(0.2)
#             spinMode += 1
#             if spinMode > 4:
#                 spinMode = 1
#        elif key == "4":
#            time.sleep(0.2)
#        elif key == "5":
#            time.sleep(0.2)
#        elif key == "6":
#            time.sleep(0.2)
#    r.value(1)

def batteryCheck():
# Read the LiPo battery voltage and display it as percentages in eyepiece circle
   global runCircle
   global lock
#   eyeLock.acquire()
   batteryVoltage = vsys.read_u16() * batteryCF
   batteryPercentage = 100 * ((batteryVoltage - batteryEmpty) / (batteryFull - batteryEmpty))
   print("Battery voltage:  " + str(batteryVoltage))
   print("Battery percent:  " + str(batteryPercentage))
   if 0 <= batteryPercentage <= 25:
       c1.duty_u16(brightDuty)
       c2.duty_u16(0)
       c3.duty_u16(0)
       c4.duty_u16(0)
       cC.duty_u16(0)
       print("Battery check: 0-25%")
   elif 25.0001 <= batteryPercentage <= 50:
       c1.duty_u16(brightDuty)
       c2.duty_u16(brightDuty)
       c3.duty_u16(0)
       c4.duty_u16(0)
       cC.duty_u16(0)
       print("Battery check: 25-50%")
   elif 50.0001 <= batteryPercentage <= 75:
       c1.duty_u16(brightDuty)
       c2.duty_u16(brightDuty)
       c3.duty_u16(brightDuty)
       c4.duty_u16(0)
       cC.duty_u16(0)
       print("Battery check: 50-75%")
   elif 75.0001 <= batteryPercentage <= 105:
       c1.duty_u16(brightDuty)
       c2.duty_u16(brightDuty)
       c3.duty_u16(brightDuty)
       c4.duty_u16(brightDuty)
       cC.duty_u16(0)
       print("Battery check: 75-100%")
   else: # something's wrong, show centre lights but nothing on ring
       c1.duty_u16(0)
       c2.duty_u16(0)
       c3.duty_u16(0)
       c4.duty_u16(0)
       cC.duty_u16(brightDuty)
       print("Battery check error")
#   sleep(3)
#   eyeLock.release()
   runCircle = 1

def servoScan(timer):
# Move the servo (and its LED) as if it's scanning the area
   global servoLocked
   if servoLocked == 0:
       pos = (random.randint(MIN,MAX))
       servo.duty_ns(pos)
       print("Servo random move to "+str(pos))
   else:
       servo.duty_ns(MID)
       print("Servo lock")

def distanceCheck(timer):
# Pulse the ultrasonic sensor to see if anything is close
    global servoLocked
#    trig.value(0)
#    trig.value(1)
#    time.sleep_us(2)
#    trig.value(0)
#    while echo.value()==0:
#        pulse_start = time.ticks_us()
#    while echo.value()==1:
#        pulse_end = time.ticks_us()
#    pulse_duration = pulse_end - pulse_start
#    distance = round(pulse_duration * 17165 / 1000000,0)
    distance = random.randint(1,100) # mimic distance input whislt we haven't got a sensor
    if distance < 30:
        servoLocked = 1
        cC.duty_u16(brightDuty)
        print("Near object detected")
    else:
        servoLocked = 0
        cC.duty_u16(0)
        print("No near object detected")

def circleSpin(timer): # runs on core2
    global circle
#    while True:
    eyeLock.acquire()
    if runCircle == 1:
        if spinMode == 1: # fade the two LEDs behind leader
            if circle == 1:
                c1.duty_u16(brightDuty)
                c2.duty_u16(0)
                c3.duty_u16(brightQtr)
                c4.duty_u16(brightHalf)
                print("Eyepiece LED 1 with fade")
            elif circle == 2:
                c1.duty_u16(brightHalf)
                c2.duty_u16(brightDuty)
                c3.duty_u16(0)
                c4.duty_u16(brightQtr)
                print("Eyepiece LED 2 with fade")
            elif circle == 3:
                c1.duty_u16(brightQtr)
                c2.duty_u16(brightHalf)
                c3.duty_u16(brightDuty)
                c4.duty_u16(0)
                print("Eyepiece LED 3 with fade")
            elif circle == 4:
                c1.duty_u16(0)
                c2.duty_u16(brightQtr)
                c3.duty_u16(brightHalf)
                c4.duty_u16(brightDuty)
                print("Eyepiece LED 4 with fade")
                # batteryCheck()
            circle += 1
            if circle > 4:
                circle = 1
        elif spinMode == 2: # no fade behind leader LED
            if circle == 1:
                c1.duty_u16(brightDuty)
                c2.duty_u16(0)
                c3.duty_u16(0)
                c4.duty_u16(0)
                print("Eyepiece LED 1")
            elif circle == 2:
                c1.duty_u16(0)
                c2.duty_u16(brightDuty)
                c3.duty_u16(0)
                c4.duty_u16(0)
                print("Eyepiece LED 2")
            elif circle == 3:
                c1.duty_u16(0)
                c2.duty_u16(0)
                c3.duty_u16(brightDuty)
                c4.duty_u16(0)
                print("Eyepiece LED 3")
            elif circle == 4:
                c1.duty_u16(0)
                c2.duty_u16(0)
                c3.duty_u16(0)
                c4.duty_u16(brightDuty)
                print("Eyepiece LED 4")
            circle += 1
            if circle > 4:
                circle = 1
        elif spinMode == 3:
            c1.duty_u16(brightDuty)
            c2.duty_u16(brightDuty)
            c3.duty_u16(brightDuty)
            c4.duty_u16(brightDuty)
            print("Eyepiece static")
        elif spinMode == 4:
            c1.duty_u16(0)
            c2.duty_u16(0)
            c3.duty_u16(0)
            c4.duty_u16(0)
            print("Eyepiece LEDs off")
            
    eyeLock.release()

def ledFlash(timer):
    for x in ledList:
        rndLED = random.randint(1,10)
        if rndLED >= 6:
            eval(x).duty_u16(brightDuty)
        else:
            eval(x).duty_u16(brightQtr)

def core1_thread():
# Triggered by the main code below, let core 1 handle the eyepiece circle LEDs, and random scan motion of the servo
    timCircle.init(period=1000, callback=circleSpin)
    timServo.init(period=750, callback=servoScan)

def buttonCheck(timer):
    buttonRead(colList,rowList)
        
# EXECUTE
# We're all setup, now get things started!
# On core 0, start the random LED flashes, distance scanning, and button scanning
#led1.duty_u16(0)
#while True:
#    batteryCheck()
#    sleep(10)
#    print(" ")

timLED.init(freq=15, callback=ledFlash)
timDistance.init(freq=1, callback=distanceCheck)
#timButtons.init(freq=1000, callback=buttonCheck)

# On core 1, run the eyepiece LED circle and servo motion
_thread.start_new_thread(core1_thread,())
