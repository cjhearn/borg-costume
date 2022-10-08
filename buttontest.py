from machine import Pin
rowpin1 = Pin(11, Pin.IN)
rowpin2 = Pin(10, Pin.IN)
rowpin3 = Pin(13, Pin.IN)
colpin1 = Pin(14, Pin.OUT)
colpin2 = Pin(15, Pin.OUT)
colpin1.value(1)
colpin2.value(1)

while True:
    print("R1 = " + str(rowpin1.value()))
    print("R2 = " + str(rowpin2.value()))
    print("R3 = " + str(rowpin3.value()))