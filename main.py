################
# BORG COSTUME #
# Chris Hearn  #
# 2022         #
################

# Wishlist
# Charging progress indicators? Maybe use the onboard LED to indicate charging level through flashes?


from machine import ADC, Pin, PWM, Timer
from time import sleep
import utime
import _thread
import random

# SETUP
# LEDs
brightLevel = 2 # 5 steps of 13005, default = 3 = 39015 = 60%
# we've moved the setting of individual levels to a function, set later
ledList = ["led1"]
led1 = PWM(Pin(25))
timLED = Timer()

# Battery
batteryFull = 4.28
batteryEmpty = 2.75
vsys = ADC(29)
batteryCharging = Pin(24, Pin.IN)
batteryCF = 3 * 3.3 / 65535
timBatt = Timer()

# Eyepiece LED circle 
eyeLock = _thread.allocate_lock()
circle = 1
runCircle = True
spinMode = 1 # 1 = with fade, 2=no fade, 3=full on static, 4=off
c1 = PWM(Pin(18))
c2 = PWM(Pin(19))#20
c3 = PWM(Pin(21))#21
c4 = PWM(Pin(20))#19
cC = PWM(Pin(17))
c1.freq(1000)
c2.freq(1000)
c3.freq(1000)
c4.freq(1000)
cC.freq(1000)
timCircle = Timer()


# Servo
MIN = 900000 # was 450000
MID = 1500000
MAX = 1600000
pos = MID
servo = PWM(Pin(22))
servo.freq(50)
servo.duty_ns(MID)
servoLocked = False
timServo = Timer()
runServo = True

# Ultrasonic Distance Sensor
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN, Pin.PULL_DOWN)
ultraPower = Pin(4, Pin.OUT)
ultraPower.high()
timDistance = Timer()

# Button breakout board
rows = [11,10,13]
cols = [14,15]
KEY_UP   = const(0)
KEY_DOWN = const(1)
keys = [['1', '2'],['3','4'],['5', '6']] # each tuple represents a row

row_pins = [Pin(pin_name, mode=Pin.IN) for pin_name in rows]
col_pins = [Pin(pin_name, mode=Pin.OUT, pull=Pin.PULL_UP) for pin_name in cols]
# row_pins = [Pin(pin_name, mode=Pin.OUT) for pin_name in rows]
# col_pins = [Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in cols]

timButtons = Timer()

def brightSet():
# Set the duty phases for the LEDs. This function gets called once at power on, then with every push of the brightness adjust button
    global brightLevel
    global brightDuty
    global brightHalf
    global brightQtr
    brightDuty = brightLevel * 13005
    brightHalf = round(brightDuty / 2)
    brightQtr = round(brightDuty / 4)    

def buttonInit():
# Set the pins for the breakout button board
    for row in range(0,3):
        for col in range(0,2):
            row_pins[row].low()

def buttonRead(timer):
# Scan the breakout button board for pushes, and trigger an action
    global brightLevel
    global runServo
    global spinMode
    key = None
    for row in range(3):
        for col in range(2):
            row_pins[row].high()
            if col_pins[col].value() == KEY_DOWN:
                key = KEY_DOWN
            if col_pins[col].value() == KEY_UP:
                key = KEY_UP
            row_pins[row].low()
            if key == KEY_DOWN:
                print("Key pressed = "+ keys[row][col])
                last_key_press = keys[row][col]
                if last_key_press == "1": # check battery level
                    sleep(0.2)
                    runCircle = False
                    batteryCheck()
                elif last_key_press == "2": # LED brightness
                    sleep(0.2)
                    print("Brightness level was " + str(brightLevel))
                    brightLevel += 1
                    if brightLevel > 3:
                        brightLevel = 1
                    brightSet()
                    print("Brightness level now " + str(brightLevel))
                elif last_key_press == "3": # eyepiece spin mode
                    sleep(0.2)
                    spinMode += 1
                    if spinMode > 4:
                        spinMode = 1
                    print("Eyepiece spin mode now " + str(spinMode))
                elif last_key_press == "4": # start / stop servo scanning
                    sleep(0.2)
                    if runServo == True:
                        runServo = False
                        servo.duty_ns(MID)
                    else:
                        runServo = True
                elif last_key_press == "5":
                   sleep(0.2)
                elif last_key_press == "6":
                   sleep(0.2)

def batteryCheck():
# Read the LiPo battery voltage and display it as percentages in eyepiece circle
   global runCircle
   eyeLock.acquire()
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
   sleep(3)
   eyeLock.release()
   runCircle = True

def batteryAutoCheck(timer):
# Read the LiPo battery voltage every 10 minutes and reduce brightness if necessary
    global brightLevel
    batteryVoltage = vsys.read_u16() * batteryCF
    batteryPercentage = 100 * ((batteryVoltage - batteryEmpty) / (batteryFull - batteryEmpty))
    if 0 <= batteryPercentage <= 20:
        newBright = 1
    elif 20.0001 <= batteryPercentage <= 40:
        newBright = 2
    elif 40.0001 <= batteryPercentage <= 60:
        newBright = 3
    elif 60.0001 <= batteryPercentage <= 80:
        newBright = 4
    elif 80.0001 <= batteryPercentage <= 105:
        newBright = 5
    else: # something's wrong, go to minimum brightness just in case
        newBright = 1
    if brightLevel > newBright:
        brightLevel = newBright

def servoScan(timer):
# Move the servo (and its LED) as if it's scanning the area
    global servoLocked
    global pos
    if runServo == True:
        if servoLocked == False:
            posmin = pos * 0.7
            posmax = pos * 1.3
            if posmin < MIN:
                posmin = MIN
            if posmax > MAX:
                posmax = MAX
            #pos = (random.randint(int(posmin),int(posmax)))
            pos = random.randint(MIN,MAX)
            servo.duty_ns(pos)
#             print("Servo random move to "+str(pos))
        else:
            servo.duty_ns(MID)
#             print("Servo lock")

def distanceCheck(timer):
# Pulse the ultrasonic sensor to see if anything is close
    global servoLocked
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(2)
    trigger.low()
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
#    print("The distance from object is ",distance,"cm")

    if distance < 50:
        servoLocked = True
        cC.duty_u16(brightDuty)
        print("Near object detected")
    else:
        servoLocked = False
        cC.duty_u16(0)
#        print("No near object detected")

def circleSpin(timer):
# Runs on core 1. Controls the LEDs in the eyepiece.
    global circle
    global brightDuty
    global brightQtr
    global brightHalf
    global brightLevel
    print("Bright level = " + str(brightLevel) + "; bright duty = " + str(brightDuty) + "; bright half = " + str(brightHalf) + "; bright qtr = " + str(brightQtr))
    eyeLock.acquire()
    if runCircle == True:
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
        elif spinMode == 3: # all LEDs stay on
            c1.duty_u16(brightDuty)
            c2.duty_u16(brightDuty)
            c3.duty_u16(brightDuty)
            c4.duty_u16(brightDuty)
            print("Eyepiece static")
        elif spinMode == 4: # all LEDs stay off
            c1.duty_u16(0)
            c2.duty_u16(0)
            c3.duty_u16(0)
            c4.duty_u16(0)
            print("Eyepiece LEDs off")
            
    eyeLock.release()

def ledFlash(timer):
# Randomly flicker the additional LEDs to give a HDD or network activity-style effect
    for x in ledList:
        rndLED = random.randint(1,10)
        if rndLED >= 6:
            eval(x).duty_u16(round(brightDuty / 6))
        else:
            eval(x).duty_u16(round(brightQtr / 6))

def core1_thread():
# Triggered by the main code below, let core 1 handle the eyepiece circle LEDs, and random scan motion of the servo
    timCircle.init(period=1000, callback=circleSpin)
    timServo.init(period=750, callback=servoScan)
#    timBatt.init(period=600000, callback=batteryAutoCheck)
        
# EXECUTE
# We're all setup, now get things started!
# First, let's set some more initial variables, and initialise the breakout button board
brightSet()
buttonInit()

# On core 0, start the random LED flashes, distance scanning, and button scanning
timLED.init(freq=15, callback=ledFlash)
timDistance.init(freq=1, callback=distanceCheck)
timButtons.init(freq=4, callback=buttonRead)

# On core 1, run the eyepiece LED circle and servo motion
_thread.start_new_thread(core1_thread,())

