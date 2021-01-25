import serial

print("Read")

with serial.Serial('/dev/ttyS5', 115200) as ser:
    while True:
        data = bytearray(ser.read(8))
        for byte in range(len(data)):
            if data[byte] >= 255:
                data[byte] = 0
            else:
                data[byte] = data[byte] + 1

        ser.write(data)

