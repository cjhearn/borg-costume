################
# BORG COSTUME #
# Chris Hearn  #
# 2022         #
################

from machine import ADC, Pin, PWM, Timer
from time import sleep
import _thread
import gc # garbage collection

# SETUP

# Timers
#1 Eyepiece circle LEDs       #8 Random LEDs
#2 Servo                      #9
#3 RESERVED                  #10
#4 Ultrasonic sensor         #11
#5 RESERVED                  #12
#6 RESERVED                  #13
#7 Buttons                   #14

# LEDs
brightLevel = 3 # 5 steps of 13005, default = 3 = 39015 = 60%
brightDuty = brightLevel * 13005
ledList = [25] # list of pins occupied by random LEDs. 25 = onboard
for x in ledList:
   led[x] = PWM(Pin([x]))
timLED = Timer(8)

# Battery
batteryFull = 4.2
batteryEmpty = 2.8
vsys = ADC(29)
batteryCharging = Pin(24, Pin.IN)
batteryCF = 3 * 3.3 / 65535

# Eyepiece LED circle 
eyeLock = _thread.allocate_lock()
circle = 1
runCircle = 1
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
timCircle = Timer(1)


# Servo
MIN = 1000000
MID = 1500000
MAX = 2000000
servo = PWM(Pin(15))
servo.freq(50)
servo.duty_ns(MID)
servoLocked = 0
timServo = Timer(2)

# Ultrasonic Distance Sensor
trig = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN, Pin.PULL_DOWN)
timDistance = Timer(4)

# Button breakout board
rowList = [1,2,3]
colList = [4,5]

for x in range(0,2):
    rowList[x] = Pin(rowList[x], Pin.OUT)
    rowList[x].value(1)
    
for x in range(0,1):
    colList[x] = Pin(colList[x], Pin.IN, Pin.PULL_UP)

keyMap = [["6","5"],["4","3"],["2","1"]]

timButtons = Timer(7)

def buttonRead(cols,rows):
    global brightLevel
    for r in rows:
        r.value(0)
        result = [cols[0].value(), cols[1].value()]
        
    if min(result) == 0:
        key = keyMap[int(rows.index(r))][int(result.index(0))]
        r.value(1)
        print("Button "+key+" pressed")
        if key == "1": # Check battery level
            time.sleep(0.2)
            runCircle = 0
            batteryCheck()

        elif key == "2": # LED brightness
            time.sleep(0.2)
            brightLevel += 1
            if brightLevel > 5:
                brightLevel = 1
                
        elif key == "3":
            time.sleep(0.2)
        elif key == "4":
            time.sleep(0.2)
        elif key == "5":
            time.sleep(0.2)
        elif key == "6":
            time.sleep(0.2)
    r.value(1)

def batteryCheck():
# Read the LiPo battery voltage and display it as percentages in eyepiece circle
    global runCircle
    global lock
    eyeLock.acquire()
    batteryVoltage = vsys.read_u16() * batteryCF
    batteryPercentage = 100 * ((batteryVoltage - batteryEmpty) / (batteryFull - batteryEmpty))
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
    elif 75.0001 <= batteryPercentage <= 100:
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
    time.sleep(3)
    eyeLock.release()
    runCircle = 1

def servoScan():
# Move the servo (and its LED) as if it's scanning the area
    global servoLocked
    if servoLocked == 0:
        pos = (random.randint(10,20) * 100000)
        servo.duty_ns(pos)
        print("Servo random move")
    else:
        servo.duty_ns(MID)
        print("Servo lock")

def distanceCheck():
# Pulse the ultrasonic sensor to see if anything is close
    global servoLocked
    trig.value(0)
    trig.value(1)
    time.sleep_us(2)
    trig.value(0)
    while echo.value()==0:
        pulse_start = time.ticks_us()
    while echo.value()==1:
        pulse_end = time.ticks_us()
    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17165 / 1000000,0)
    if distance < 50:
        servoLocked = 1
        cC.duty_u16(brightDuty)
        print("Near object detected")
    else:
        servoLocked = 0
        cC.duty_u16(0)
        print("No near object detected")

def circleSpin(): # runs on core2
    global circle
    eyeLock.acquire()
    if runCircle == 1:
        match circle:
            case [1]:
                c1.duty_u16(brightDuty)
                c2.duty_u16(0)
                c3.duty_u16(0)
                c4.duty_u16(0)
                print("Eyepiece LED 1")
            case [2]:
                c1.duty_u16(0)
                c2.duty_u16(brightDuty)
                c3.duty_u16(0)
                c4.duty_u16(0)
                print("Eyepiece LED 2")
            case [3]:
                c1.duty_u16(0)
                c2.duty_u16(0)
                c3.duty_u16(brightDuty)
                c4.duty_u16(0)
                print("Eyepiece LED 3")
            case [4]:
                c1.duty_u16(0)
                c2.duty_u16(0)
                c3.duty_u16(0)
                c4.duty_u16(brightDuty)
                print("Eyepiece LED 4")
                circle = 1
    eyeLock.release()
    gc.collect()

def ledFlash():
    for x in ledList:
        rndLED = random.randint(1,10)
        if rndLED >= 6:
            led[x].duty_u16(brightduty)
        else:
            led[x].duty_u16(0)

def core1_thread():
# Triggered by the main code below, let core 1 handle the eyepiece circle LEDs, and random scan motion of the servo
    timCircle.init(freq=50, period=500, mode=Timer.PERIODIC, callback=circleSpin())   
    timServo.init(freq=50, period=500, mode=Timer.PERIODIC, callback=servoScan())


# EXECUTE
# We're all setup, now get things started!
# On core 0, start the random LED flashes, distance scanning, and button scanning
timLED.init(freq=2, mode=Timer.PERIODIC, callback=ledFlash)
timDistance.init(freq=50, period=2000, mode=Timer.PERIODIC, callback=distanceCheck())
timButtons.init(freq=1000, callback=buttonRead(colList,rowList))

# On core 1, run the eyepiece LED circle and servo motion
core1 = _thread.start_new_thread(core1_thread, ())
