import os
import serial
import time


ser = serial.Serial('/dev/ttyS5', 921600)

data = os.urandom(1024*1024)
byte_data = bytearray(data)

print("sending")
ser.write(byte_data)
print("sended")

take_data = ser.read(1024*1024)
if take_data == data:
    print("True")
else:
    print("False")
